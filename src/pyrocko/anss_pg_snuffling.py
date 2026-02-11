from sqlalchemy import create_engine
import pandas as pd
from obspy import UTCDateTime
from obspy.core.util.attribdict import AttribDict
from pyrocko.gui.snuffler.snuffling import Snuffling, Param, PhaseMarker, Switch, Choice, EventMarker
from pyrocko.gui.snuffler.pile_viewer import Marker, EventMarker, PhaseMarker, qc
from pyrocko.model.event import Event
from pyrocko.gui.snuffler.marker import associate_phases_to_events

def rflag2kind(rflag, showhelp=False):
    if showhelp:
        return """
        ORIGIN.rflag to EventMarker.kind mapping:
                 (Finalized) f/F = 2 (BLUE)
            (Human Reviewed) h/H = 3 (ORANGE)
           (Human Inspected) i/I = 4 (PURPLE)
                       (???) c/C = 5 (BUFF)
        (Automatic Solution) a/a = 0 (RED) 
        """
    if rflag.lower() == 'f':
        return 2
    elif rflag.lower() == 'h':
        return 3
    elif rflag.lower() == 'i':
        return 4 
    elif rflag.lower() == 'c':
        return 5
    elif rflag.lower() == 'a':
        return 0
    
def fm2polarity(fm, showhelp=False):
    if showhelp:
        return """
        ARRIVAL.fm to PhaseMarker._polarity mapping:
        'c.' = UP
        'd.' = DOWN
        '..' = None
        None = None
             = 0 (Unused, UP/DOWN marker)
        """
    if fm is None:
        return None
    elif fm in ['c.','C.','u.','U.','+.','u','U','c','C', 1]:
        return 1
    elif fm in ['d.','D.','-.','d','D','-', -1]:
        return -1
    elif fm in ['..','?','', None]:
        return None
    
def polarity2fm(polarity):
    if polarity is None:
        return None
    elif polarity == 1:
        return 'c.'
    elif polarity == -1:
        return 'd.'
    elif polarity == 0:
        return '..'
    else:
        raise ValueError
    
def quality2weight(quality):
    """
    Convert an ARRIVAL.quality measurement into
    a Jiggle/HYPO2000 phase weight label

    Weight  |   Quality
    0       |   1.0
    1       |   [0.75, 1.00)
    2       |   [0.50, 0.75)
    3       |   [0.25, 0.50)
    4       |   [0.00, 0.25)
    """
    if quality < 0.25:
        return 4
    elif 0.25 <= quality < 0.5:
        return 3
    elif 0.5 <= quality < 0.75:
        return 2
    elif 0.75 <= quality < 1.0:
        return 1
    elif quality == 1:
        return 0


def quality2kind(quality):
    if quality < 0.25:
        return 0
    elif 0.25 <= quality < 0.5:
        return 5
    elif 0.5 <= quality < 0.75:
        return 4
    elif 0.75 <= quality < 1.0:
        return 3
    elif quality == 1:
        return 2


def qual2str(qual):
    if qual in ['e','i']:
        return qual
    else:
        return ''

class ANSSArrival(AttribDict):
    _types = {
        'event_hash': (type(None), str),
        'evid': (type(None), int),
        'orid': (type(None), int),
        'arid': (type(None), int),
        'commid': (type(None), int),
        'datetime': float,
        'sta': str,
        'net': str,
        'auth': str,
        'subsource': str,
        'channel': (type(None), str),
        'channelsrc': (type(None), str),
        'seedchan': (type(None), str),
        'location': (type(None), str),
        'iphase': (type(None), str),
        'qual': (type(None), str),
        'clockqual': (type(None), int),
        'clockcorr': (type(None), float),
        'ccset': (type(None), float),
        'fm': (type(None), str),
        'ema': (type(None), float),
        'azimuth': (type(None), float),
        'slow': (type(None), float),
        'deltim': (type(None), float),
        'delinc': (type(None), float),
        'delaz': (type(None), float),
        'delslo': (type(None), float),
        'quality': (type(None), float),
        'snr': (type(None), float),
        'rflag': str,
        'lddate': UTCDateTime
    }
    defaults = {
        'event_hash': None,
        'event': None,
        'orid': None,
        'arid': None,
        'commid': None,
        'sta': '',
        'net': '',
        'auth': '',
        'subsource': 'Snuffler',
        'channel': None,
        'channelsrc': None,
        'seedchan': None,
        'location': '  ',
        'iphase': None,
        'qual': None,
        'clockqual': None,
        'clockcorr': None,
        'ccset': None,
        'fm': None,
        'ema': None,
        'azimuth': None,
        'slow': None,
        'deltim': None,
        'delinc': None,
        'delaz': None,
        'delslo': None,
        'quality': 0.,
        'snr': None,
        'rflag': 'a',
        'lddate': UTCDateTime()
    }
    def __init__(self, values={}):
        super().__init__(values)

class ANSSOrigin(AttribDict):
    _types = {
        'event_hash': (type(None), str),
        'evid': (type(None), int),
        'etype': str,
        'version': int,
        'selectflag': int,
        'orid': (type(None), int),
        'prefmag': (type(None), int),
        'prefmec': (type(None), int),
        'commid': (type(None), int),
        'bogusflag': (int, type(None)),
        'datetime': (float, type(None)),
        'lat': (float, type(None)),
        'lon': (float, type(None)),
        'depth': (float, type(None)),
        'mdepth': (float, type(None)),
        'type': (str, type(None)),
        'algorithm': (str, type(None)),
        'algo_assoc': (str, type(None)),
        'auth': (str, type(None)),
        'subsource': (str, type(None)),
        'datumhor': (str, type(None)),
        'datumver': (str, type(None)),
        'gap': (float, type(None)),
        'distance': (float, type(None)),
        'wrms': (float, type(None)),
        'stime': (float, type(None)),
        'erhor': (float, type(None)),
        'sdep': (float, type(None)),
        'erlat': (float, type(None)),
        'erlon': (float, type(None)),
        'totalarr': (int, type(None)),
        'totalamp': (int, type(None)),
        'ndef': (int, type(None)),
        'nbs': (int, type(None)),
        'nbfm': (int, type(None)),
        'locevid': (int, type(None)),
        'quality': (float, type(None)),
        'fdepth': (str, type(None)),
        'fepi': (str, type(None)),
        'ftime': (str, type(None)),
        'vmodelid': (str, int, type(None)),
        'cmodelid': (str, int, type(None)),
        'crust_type': (str, type(None)),
        'crust_model': (str, type(None)),
        'gtype': (str, type(None)),
        'rflag': str,
        'lddate': (UTCDateTime)
    }

    defaults = {
        'event_hash': None,
        'evid': None,
        'etype': 'st',
        'version': 1,
        'selectflag': 0,
        'orid': None,
        'prefmag': None,
        'prefmec': None,
        'commid': None,
        'bogusflag': 1,
        'datetime': None,
        'lat': None,
        'lon': None,
        'depth': None,
        'mdepth': None,
        'type': None,
        'algorithm': None,
        'algo_assoc': 'Snuffler',
        'auth': None,
        'subsource': 'Snuffler',
        'datumhor': None,
        'datumver': None,
        'gap': None,
        'distance': None,
        'wrms': None,
        'stime': None,
        'erhor': None,
        'sdep': None,
        'erlat': None,
        'erlon': None,
        'totalarr': None,
        'totalamp': None,
        'ndef': None,
        'nbs': None,
        'nbfm': None,
        'locevid': None,
        'quality': None,
        'fdepth': 'y',
        'fepi': 'y',
        'ftime': 'y',
        'vmodelid': None,
        'cmodelid': None,
        'crust_type': None,
        'crust_model': None,
        'gtype': None,
        'rflag': 'a',
        'lddate': UTCDateTime()
    }

    def __init__(self, values={}):
        # if passing a dictionary
        if isinstance(values, dict):
            vals = {}
            for _k, _v in values.items():
                if _k in self.defaults.keys():
                    vals.update({_k:_v})
        # if passing a pyrocko.model.event.Event
        elif isinstance(values, Event):
            vals = {
                'lat': values.lat,
                'lon': values.lon,
                'datetime': values.time,
                'depth': values.depth,
                'auth': values.catalog,
                'event_hash': values.get_hash(),
            }
            if hasattr(values, 'extras'):
                if isinstance(values.extras, dict):
                    for _k, _v in values.extras.items():
                        if _k in self._types.keys():
                            vals.update({_k: _v})
        else:
            raise TypeError
        super().__init__(vals)

                            

class ArrivalMarker(PhaseMarker):
    def __init__(self, phase_marker=None, **options):
        
        self._in = ANSSArrival()
        for _k, _v in options.items():
            if _k in self._init.keys():
                self._init.update({_k:_v})
        # If no phase marker is provided
        if phase_marker is None:
            if self._in.location == '  ':
                _loc = ''
            else:
                _loc = self._in.location
            
            if self._in.channel is None and self._in.seedchan is None:
                raise ValueError('Channel must be specified with either "seedchan" or "channel"')
            elif self._in.seedchan is None:
                _cha = self._in.channel
            else:
                _cha = self._in.seedchan

            _ikw = {
                'nslc_ids':((self._in.net, self._in, _loc, _cha),),
                'tmin':self._in.datetime,
                'tmax':self._in.datetime,
                'phasename': self._in.iphase,
                'polarity': fm2polarity(self._in.fm),
                'automatic': self._in.rflag.lower() in ['a','c','i'],
                'incidence_angle': self._in.ema
            }
            for _key in ['kind','event','event_hash','event_time']:
                if _key in options.keys():
                    _ikw.update({_key: options[_key]})
            super().__init__(**_ikw)
            if isinstance(self._event_hash, str):
                self._in.event_hash=self._event_hash

        # If phasemarker is provided
        elif isinstance(phase_marker, PhaseMarker):
            # If it is already an ArrivalMarker, return input unaltered
            if isinstance(phase_marker, ArrivalMarker):
                return phase_marker
            if len(phase_marker.nslc_ids) != 1:
                raise AttributeError(f'Can only convert single-entry nslc_ids PhaseMarkers. This has {len(phase_marker.nslc_ids)} nslc_ids entries')
            super().__init__(
                nslc_ids=phase_marker.nslc_ids,
                tmin=phase_marker.tmin,
                tmax=phase_marker.tmax,
                kind=phase_marker.kind,
                event=phase_marker._event,
                event_hash=phase_marker._event_hash,
                event_time=phase_marker._event_time,
                automatic=phase_marker._automatic,
                incidence_angle=phase_marker._incidence_angle,
                takeoff_angle=phase_marker._takeoff_angle,
                polarity=phase_marker._polarity
            )
            n, s, l, c = self.nslc_ids[0]
            if l == '':
                _l = '  '
            else:
                _l = l
            values={
                'net': n,
                'sta': s,
                'location': _l,
                'seedchan': c,
                'channel': c,
                'datetime': 0.5*(self.tmin + self.tmax),
                'event_hash': self.get_event_hash(),
                'fm': polarity2fm(self.get_polarity()),
                'iphase': self.get_phasename(),
                'ema': self._incidence_angle,
            }
            if not self._automatic:
                if self.kind != 0 and self.phasename is not None:
                    values.update({'rflag': 'h'})
                elif self.kind == 0 and self.phasename is not None:
                    values.update({'rflag': 'i'})
                    self._automatic=True
                else:
                    self._automatic=True
            
            self._in = ANSSArrival(values=values)
        # Mark all fields as not updated
        self._updated = {_k: False for _k in self._in.keys()}
    
    def set_event_hash(self, event_hash):
        self.check_updates()
        super().set_event_hash(event_hash)

    def set_phasename(self, phasename):
        self.check_updates()
        super().set_phasename(phasename)
    
    def set_polarity(self, polarity):
        self.check_updates()
        super().set_polarity(polarity)

    # FIXME: Convert this to a __setattr__ at some point.
    def check_updates(self):
        if not hasattr(self, '_updated'):
            return
        
        # Check datetime
        if self._in.datetime == 0.5*(self.tmin + self.tmax):
            # If matched, ensure that datetime does not show as alteration
            self._updated.datetime=False
            # If arid was modified, revert
            if self._updated.arid != self._in.arid:
                self._updated.arid = False
            # If orid was modified, revert
            if self._updated.orid != self._in.orid:
                self._updated.orid = False
        # Enforce several updates reflecting that this marker no longer
        # represents the same NSLC+T entry
        else:
            self._updated.datetime = 0.5*(self.tmin + self.tmax)
            if self._in.rflag.lower() not in ['h','f']:
                self._updated.rflag='h'
            if self._in.arid is not None:
                self._updated.arid=None
            if self._in.orid is not None:
                self._updated.orid=None

        # Phase label update
        if self.phasename != self._in.iphase:
            self._updated.iphase = self._phasename
        # Reset clause
        elif self._updated.iphase:
            self._updated.iphase = False

        # Polarity update check
        if polarity2fm(self._polarity) != self._in.fm:
            self._updated.fm = polarity2fm(self._polarity)
        # Reset clause
        elif self._updated.fm:
            self._updated.fm = False

        # Kind check for rflag
        if self.kind != 0:
            # If marker KIND is paired with any changes in phase label, polarity, or time
            # elevate to 'h'
            if any([self._updated.iphase, self._updated.fm, self._updated.datetime]):
                if self._in.rflag.lower() != 'h':
                    self._updated.rflag='h'
            # If not, but label color is changed on an 
            elif self._automatic and self._updated.rflag.lower() != 'i':
                self._updated.rflag='i'

class OriginMarker(EventMarker):
    def __init__(self, event_marker=None, **options):
        if event_marker is None:
            # If an event is provided, scrape that first
            if 'event' in options.keys():
                if isinstance(options['event'], Event):
                    self._in = ANSSOrigin(options['event'])
                    super().__init__(event=options['event'],
                                    )
                else:
                    options.pop('event')
            else:
                self._in = ANSSOrigin(options)
        # If an OriginMarker is provided, do nothing
        elif isinstance(event_marker, OriginMarker):
            return event_marker
        # If an event marker is provided, scrape data and run update
        elif isinstance(event_marker, EventMarker):
            super().__init__(event=event_marker._event,
                             kind=event_marker.kind,
                             event_hash=event_marker._event.get_hash()
                             )
            self._in = ANSSOrigin(event=event_marker._event)
            
            




class ANSS_PostgreSQL_Client(Snuffling):
    """
    Display preferred origins and assocaited phase arrivals present
    in an ANSS parametric schema PostgreSQL database on visible channels
    and times within an Snuffler interface.
    """
    # Allow pile changed notifications
    # Snuffling.enable_pile_changed_notifications()
    # Snuffling.set_have_pile_changed_hook(True)


    def __init__(self, dbname='my_anss_pgdb', user='browser', port=5432, host='localhost',password=None):
        # Compose connection kwargs
        self.pgkw = {'dbname': dbname,
                     'dbuser': user,
                     'dbport': port,
                     'dbhost': host,
                     'dbpass': password}
        # Create cache attributes
        self._cached_event_markers=[]
        self._current_event = None
        self._cached_etypes = []
        self._orid2hash = {}
        self._hash2orid = {}
        # Inherit
        Snuffling.__init__(self)

    
    def setup(self):
        # Provide display name
        self.set_name("ANSS PostgreSQL Catalog Viewer")
        # Auto-update by default
        self.set_live_update(True)

        # Add Preferred Origins Only Switch
        self.add_parameter(
            Switch(
                'Preferred Origins Only',
                'prefor_only',
                default=True
            )
        )
        # Add event types selectors
        self.add_parameter(
            Switch(
                'Include EQ',
                'inceq',
                default=True
            )
        )

        self.add_parameter(
            Switch(
                'Include SU',
                'incsu',
                default=False
            )
        )
        self.add_parameter(
            Switch(
                'Include PX',
                'incpx',
                default=False
            )
        )

        self.add_parameter(
            Switch(
                'Include LF',
                'inclf',
                default=False
            )
        )

        self.add_parameter(
            Switch(
                'Include ST',
                'incst',
                default=False
            )
        )
        self.add_parameter(
            Switch(
                'Include UK',
                'incuk',
                default=False
            )
        )
        # Create database connection
        if self.pgkw['dbpass'] is None:
            self.engine = create_engine("postgresql://{dbuser}@{dbhost}:{dbport}/{dbname}".format(**self.pgkw))
        else:
            self.engine = create_engine("postgresql://{dbuser}:{dbpass}@{dbhost}:{dbport}/{dbname}".format(**self.pgkw))
        # Scrape for all unique origin authors
        df_auth = pd.read_sql(
            "SELECT auth, count(*) FROM origin GROUP BY auth ORDER BY count DESC;",
            self.engine)
        auths = tuple([_e for _e in df_auth.auth] + ['all'])
        # Scrape for all unique origin subsources
        df_subsrc = pd.read_sql(
            "SELECT subsource, count(*) FROM origin GROUP BY subsource ORDER BY count DESC;",
            self.engine
        )
        subsrcs = tuple([_e for _e in df_subsrc.subsource] + ['all'])
        # Create selection drop-downs for origin author(s) and subsource(s)
        self.add_parameter(
            Choice(
                "Catalog Author",
                'auth',
                default=auths[0],
                choices=auths
            )
        )
        self.add_parameter(
            Choice(
                "Origin Subsource",
                "subsource",
                default='all',
                choices=subsrcs
            )
        )


    def get_current_etypes(self):
        # Gather etypes to load
        etypes = []
        if self.inceq:
            etypes.append('eq')
        if self.incsu:
            etypes.append('su')
        if self.incpx:
            etypes.append('px')
        if self.incst:
            etypes.append('st')
        if self.incuk:
            etypes.append('uk')
        if self.inclf:
            etypes.append('lf')
        if etypes == []:
            etypes = self._cached_etypes
        return etypes


    def cache_event_markers(self):
        # Check if any additional event/origin entries
        # should be read into the cache

        # Connect to viewer and pile
        viewer = self.get_viewer()
        pile = self.get_pile()
        # Get time range of loaded traces
        TMIN = pile.get_tmin()
        TMAX = pile.get_tmax()
        # Check if there are NEW etypes being requested
        _etypes = self.get_current_etypes()
        etypes = []
        for _e in _etypes:
            if _e in self._cached_etypes:
                continue
            self._cached_etypes.append(_e)
            etypes.append(_e)
        # Send fail message if no etypes are specified or cached
        if etypes == [] and self._cached_etypes == []:
            self.fail(
                'Must have at least one event type selected to query catalog'
            )
        # Compose SQL suffix if there is a single EVENT.etype requested
        elif len(etypes) == 1:
            suffix = f"AND e.etype = '{etypes[0]}' "
        # Compose SQL suffix if there are multiple EVENT.etype's are requested
        elif len(etypes) > 1:
            suffix = f"AND e.etype IN {str(tuple(etypes))} "
        # Otherwise, grab cached etypes and return no new markers
        else:
            etypes = self._cached_etypes
            return []
        # If using all authors, cap-off the SQL
        if self.auth == 'all':
            suffix += ';'
        # If using a specific ORIGIN.auth, add to SQL WHERE clause and then cap-off
        else:
            suffix += f"    AND o.auth='{self.auth}';"
        # Create primary EVENT/ORIGIN truncated query
        sql = """
            SELECT 
                e.evid,
                e.etype,
                e.version,
                e.selectflag,
                o.orid,
                o.bogusflag,
                TrueTime.getEpoch(o.datetime, 'UNIX') AS datetime,
                o.lat,
                o.lon,
                o.depth,
                o.mdepth,
                o.type,
                o.algorithm,
                o.algo_assoc,
                o.auth,
                o.subsource,
                o.datumhor,
                o.datumver,
                o.gap,
                o.distance,
                o.wrms,
                o.stime,
                o.erhor,
                o.sdep,
                o.erlat,
                o.erlon,
                o.totalarr,
                o.nbs,
                o.nbfm,
                o.locevid,
                o.quality,
                o.fdepth,
                o.fepi,
                o.ftime,
                o.vmodelid,
                o.cmodelid,
                o.crust_type,
                o.crust_model,
                o.gtype,
                o.rflag,
                m.magnitude AS mag,
                'm'||m.magtype AS magtype
        """
        # Apply preferred origin filter in query as join
        if self.prefor_only:
            sql += """
            FROM event e INNER JOIN origin o ON e.prefor = o.orid 
            """
        # Apply de-select "preferred origins only" filter in query as join
        else:
            sql += """
            FROM origin o INNER JOIN event e ON o.evid = e.evid 
            """
        sql += """
            LEFT JOIN netmag m ON o.prefmag = m.magid 
        WHERE o.datetime >= TrueTime.putEpoch(%(tmin)s, 'UNIX') 
            AND o.datetime <= TrueTime.putEpoch(%(tmax)s, 'UNIX') 
        """
        sql += suffix
        # ACTUALLY QUERY THE DATABASE
        df_eo = pd.read_sql(sql, self.engine, index_col='orid',
                            params = {'tmin': TMIN, 'tmax': TMAX})
        # Compose new EventMarkers
        markers = []
        for orid, eorow in df_eo.iterrows():

            # Skip if the ORID has already been loaded
            if orid in self._orid2hash.keys():
                continue
            # Otherwise compose as an origin marker
            omark = OriginMarker(orid=orid, **eorow.to_dict())

            self._orid2hash.update({orid: omark.get_event_hash()})
            self._hash2orid.update({omark.get_event_hash(): orid})
            markers.append(omark)
            self._cached_event_markers.append(omark)

        return markers
   
   
        
    def on_active_event_changed(self):
        """Method called when the active event marker change
        signal is emminated from the PileViewer. See connection
        set up in the :meth:`~.
        """        
        v = self.get_viewer()
        active_event, phase_markers = self.get_active_event_and_phase_markers()
        if active_event is not None:
            if phase_markers == []:
                print(f'loading ORID {active_event._event.extras["orid"]} arrivals from database')
                phase_markers = self.load_assocated_arrials(active_event)
                self.add_markers(phase_markers)
            # else:
                # print('arrivals already loaded')

    def load_assocated_arrials(self, event_marker):
        orid = self._hash2orid[event_marker.get_event_hash()]
        sql = """
        SELECT 
            x.orid, 
            a.arid,
            TrueTime.getEpoch(a.datetime, 'UNIX') AS datetime,
            a.net,
            a.sta,
            CASE WHEN a.location='  ' THEN '' ELSE a.location END AS location,
            a.seedchan, 
            a.iphase,
            a.qual,
            a.quality,
            a.fm,
            a.rflag, 
            a.lddate,

        FROM assocaro x INNER JOIN arrival a ON x.arid = a.arid 
            WHERE x.orid = %(orid)s;
        """
        df_aa = pd.read_sql(sql, self.engine, params={'orid': int(orid)})
        markers = []
        for arid, arow in df_aa.iterrows():
            ehash = event_marker.get_event_hash()
            amark = ANSSArrival(event_hash=ehash, arid=arid, **arow)
            markers.append(amark)
        return markers


    def call(self):
        v = self.get_viewer()
        _current_event = v.get_active_event_marker()
        self.cleanup()
        self.get_viewer().clean_update()
        # Update cache
        self.cache_event_markers()
        # (Re)add markers from cache
        include = []
        # Get current event type selection from radio buttons
        current_etypes = self.get_current_etypes()
        for m in self._cached_event_markers:
            # Fitler for event type
            if m._event.extras['etype'] in current_etypes:
                # Filter for selectflag
                if self.prefor_only and m._event.extras['selectflag'] == 0:
                    continue
                # Filter for catalog
                if self.auth != 'all' and m._event.catalog != self.auth:
                    continue
                # Filter for subsource
                if self.subsource != 'all' and m._event.extras['subsource'] != self.subsource:
                    continue
                include.append(m)
        self.add_markers(include)

        # Clause for interactive response to user activating an event marker
        v = self.get_viewer()
        v.active_event_marker_changed.connect(
            self.on_active_event_changed
        )

def __snufflings__():
    return [ANSS_PostgreSQL_Client()]
