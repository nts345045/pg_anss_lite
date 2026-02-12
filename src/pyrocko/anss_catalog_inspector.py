import os, sys
from collections import defaultdict
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine
sys.path.append(str(Path(__file__).parent))
# from anss_pg_markers import ANSSEventMarker, ANSSPhaseMarker, phase2anss, event2anss
from pyrocko.gui.snuffling import Snuffling, Switch, Choice

class ANSS_Catalog_Inspector(Snuffling):

    def __init__(
            self,
            sqlalchemy_connection_string,
            sql_alteration_file=Path().cwd()/'anss_pg_alterations.sql'
    ):
        

        Snuffling.__init__(self)
        # Create a connection to database for read-only purposes
        try:
            self.engine=create_engine(sqlalchemy_connection_string)
        except:
            self.warn(f'Failed to connect to "{sqlalchemy_connection_string}"')
        
        self._sql_out_file = sql_alteration_file
        if os.path.isfile(self._sql_out_file):
            self.warn(f'sql_alteration_file "{self._sql_out_file}" already exists. It will be overwritten!!!')

        self._cached_event_markers = []
        self._cached_phase_markers = defaultdict(list)
        self._cached_etypes = set()
        self._cached_ns = set()
        self._orid2hash = {}
        self._hash2orid = {}

    def setup(self):
        """
        Sets up the control panel for the snuffling
        Creates drop-down options for filtering events by:
        
        catalog / ORIGIN.auth
        """
        self.set_name('ANSS PostgreSQL Catalog Inspector')
        self.set_live_update(True)
        # Preferred Events Only Switch
        self.add_parameter(
            Switch(
                'Preferred Events Only',
                'selectflag1',
                default=True
            )
        )
        # Preferred Origins Only Switch
        self.add_parameter(
            Switch(
                'Preferred Origins Only',
                'prefor_only',
                default=True
            )
        )
        # Event Type Selection Switches
        self.add_parameter(
            Switch(
                'Earthquakes',
                'inceq',
                default=True
            )
        )
        self.add_parameter(
            Switch(
                'Surface Events',
                'incsu',
                default=False
            )
        )
        self.add_parameter(
            Switch(
                'Blasts',
                'incpx',
                default=False
            )
        )
        self.add_parameter(
            Switch(
                'Low Frequency',
                'inclf',
                default=False
            )
        )
        self.add_parameter(
            Switch(
                'Triggers',
                'incst',
                default=False
            )
        )
        self.add_parameter(
            Switch(
                'Other Event Types',
                'incother',
                default=False
            )
        )

        # Catalog author and origin subsource drop-downs
        df_auth_src = pd.read_sql(
            """
            SELECT auth, subsource, COUNT(*) 
            FROM origin 
            GROUP BY auth, subsource 
            ORDER BY count DESC;
            """,
            self.engine
        )
        auths = tuple([_e for _e in df_auth_src.auth.unique()] + ['all'])
        subsources = tuple([_e for _e in df_auth_src.subsource.unique()] + ['all'])

        self.add_parameter(
            Choice(
                "Catalog Author",
                'auth',
                default='all',
                choices=auths
            )
        )
        self.add_parameter(
            Choice(
                "Origin Subsource",
                'subsource',
                default='all',
                choices=subsources
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
        if self.inclf:
            etypes.append('lf')
        if self.incst:
            etypes.append('st')
        if self.incother:
            etypes += ['uk','th','av','ve','vt','nt','lp','se']
        # If none specified, check cache
        if etypes == []:
            etypes = list(self._cached_etypes)
        return etypes
    
    def cache_event_markers(self):
        pile = self.get_pile()
        # viewer = self.get_viewer()
        TMAX = pile.get_tmax()
        TMIN = pile.get_tmin()
        for n,s,l,c in pile.nslc_ids:
            # print(f'Caching {n}.{s}')
            self._cached_ns.add((n,s))
        # for sta in pile.get_stations():
        #     print(f'Station {sta} in view')
            # self._cached_ns.add((sta.network, sta.station))
        _etypes = self.get_current_etypes()
        for _e in _etypes:
            self._cached_etypes.add(_e)
        if _etypes == []:
            self.fail(
                "Must have at least one event type selected to start querying catalog."
            )

        sql = """
        SELECT 
            e.evid,
            e.etype,
            e.version,
            e.selectflag,
            e.prefor,
            e.prefmag,
            e.prefmec,
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
            m.magnitude,
            m.magtype 
        """
        if self.prefor_only:
            sql += """
            FROM event e 
                INNER JOIN origin o ON e.prefor=o.orid 
                LEFT JOIN netmag m ON e.prefmag=m.magid 
            """
        else:
            sql += """
            FROM origin o 
                INNER JOIN event e ON o.evid = e.evid 
                LEFT JOIN netmag m ON o.prefmag = m.magid 
            """
        sql += f"""
            WHERE o.datetime >= TrueTime.putEpoch({TMIN}, 'UNIX') 
                AND o.datetime <= TrueTime.putEpoch({TMAX}, 'UNIX') 
            """

        if self.selectflag1:
            sql += """
            AND e.selectflag = 1 
            """
        if len(_etypes) == 1:
            sql += f""" 
            AND e.etype = '{_etypes[0]}';
            """
        elif len(_etypes) > 1:
            sql += f"""
            AND etype IN {str(tuple(_etypes))};
            """
        df_eo = pd.read_sql(sql, self.engine, index_col='orid')
        markers = []
        # print(f'Attempting to load {len(df_eo)} event markers from database')
        for orid, row in df_eo.iterrows():
            if orid in self._orid2hash.keys():
                continue

            kwargs = row.to_dict()
            for _k, _v in row.isna().items():
                if _v:
                    kwargs.pop(_k)

            # print(f'{row.evid} {row.datetime} {row.prefor}')
            event_marker = ANSSEventMarker(orid=int(orid), **kwargs)
            ehash = event_marker.get_event_hash()
            self._orid2hash.update({orid:ehash})
            self._hash2orid.update({ehash:orid})
            markers.append(event_marker)
            self._cached_event_markers.append(event_marker)
        # print(f'Loaded {len(markers)} event markers')
        return markers
    
    def load_arrivals(self, event_marker):
        orid = self._hash2orid[event_marker.get_event_hash()]
        print(f'Loading arrivals for ORID {orid} and stations {self._cached_ns}')
        sql = f"""
        SELECT 
            x.orid,
            x.importance,
            x.delta,
            x.seaz,
            x.in_wgt,
            x.wgt,
            x.timeres,
            x.vmodelid,
            x.scorr, 
            x.sdelay,
            a.arid,
            a.commid,
            TrueTime.getEpoch(a.datetime,'UNIX') as datetime,
            a.sta,
            a.net,
            a.auth,
            a.subsource,
            a.channel,
            a.channelsrc,
            a.seedchan,
            a.location,
            a.iphase,
            a.qual,
            a.clockqual,
            a.clockcorr,
            a.ccset,
            a.fm, 
            a.ema,
            a.azimuth,
            a.slow,
            a.deltim,
            a.delinc,
            a.delaz,
            a.delslo,
            a.quality,
            a.snr,
            a.rflag,
            a.lddate 
        FROM assocaro x 
            INNER JOIN arrival a ON x.arid = a.arid 
        WHERE x.orid = {orid}; -- AND 
           -- (a.net, a.sta) IN {str(tuple(self._cached_ns))};
        """
        df_aa = pd.read_sql(sql, self.engine, index_col='arid')
        markers=[]
        for arid, row in df_aa.iterrows():
            kwargs = row.to_dict()
            for _k, _v in row.isna().items():
                if _v:
                    # print(kwargs)
                    kwargs.pop(_k)
            pmark = ANSSPhaseMarker(arid=arid, event=event_marker._event, **kwargs)
            # print(pmark.nslc_ids)
            markers.append(pmark)
        return markers
    
    def on_active_event_changed(self):
        v = self.get_viewer()
        active_event, phase_markers = self.get_active_event_and_phase_markers()
        if active_event is not None:
            if phase_markers == []:
                phase_markers = self.load_arrivals(active_event)
                # self._cached_phase_markers[active_event.get_event_hash()] += phase_markers
                self.add_markers(phase_markers)
        if active_event.active:
            # print(f'checking for alterations to {len(phase_markers)} active phase markers')
            # for m in phase_markers:
            #     if any(_v for _v in m.check_for_alterations().values()):
            #         print(f'{".".join(m.one_nslc())} | {m.check_for_alterations()}')
            active_event.compose_sql(phase_markers=phase_markers)
                # for _k, _v in m.check_for_alterations().items():
                #     if _v:
                #         print(f'{m._pg_assocaro.orid} {m._pg_arrival.arid} - {_k} CHANGED {_v}')
    
    def call(self):
        v = self.get_viewer()
        # Enable dynamic arrival loading when event markers are activated
        v.active_event_marker_changed.connect(
            self.on_active_event_changed)
        self.cleanup()
        self.get_viewer().clean_update()
        self.cache_event_markers()
        print(f'{len(self._cached_event_markers)} event markers in cache')
        include = []
        current_etypes = self.get_current_etypes()
        current_hashes = []
        print(f'Including ETYPES {current_etypes}')
        for m in self._cached_event_markers:
            
            if m._pg_event.etype.lower() not in current_etypes:
                continue
            if self.prefor_only and m._pg_origin.orid != m._pg_event.prefor:
                continue
            # print(m)

            if self.selectflag1 and m._pg_event.selectflag != 1:
                continue
            if self.auth != 'all' and m._pg_origin.auth != self.auth:
                continue
            if self.subsource != 'all' and m._pg_origin.subsource != self.subsource:
                continue
            current_hashes.append(m.get_event_hash())
            include.append(m)
        print(f'Adding {len(current_hashes)} event markers to view')
        for _h in current_hashes:
            phases = self._cached_phase_markers[_h]
            for m in phases:
                include.append(m)

        self.add_markers(include)



    # def pre_destroy(self):
    #     v = self.get_viewer()
    #     with open(self._sql_out_file, 'w') as _f:
    #         _f.write('BEGIN TRANSACTION;\n')
    #         for m in v.get_markers():
    #             if isinstance(m, ANSSEventMarker):



def __snufflings__():
    return [
        ANSS_Catalog_Inspector(
            'postgresql://browser@localhost:5445/tahoma'
        )
    ]





#### SUPPORTING CLASSES AND METHODS ####

import numpy as np
from copy import deepcopy
from pyrocko.gui.snuffler.marker import PhaseMarker, EventMarker
from pyrocko.model.event import Event
from pyrocko.model.station import Station
from obspy.core.util.attribdict import AttribDict
from obspy import UTCDateTime
from warnings import WarningMessage

class RestrictedAttribDict(AttribDict):
    primary_keys = []
    foreign_keys = []
    def __init__(self, tablename, **options):
        super().__init__({_k:_v for _k, _v in options.items()})
        # self.tablename=tablename
        # self._initial = AttribDict({_k:_v for _k, _v in self.copy().items()})

    def __setattr__(self, key, value):
        if key in self.defaults.keys():
            if str(value) == 'nan':
                value = None
            if value in [None, pd.NaT, np.nan, float('nan')]:
                value = None
            super().__setattr__(key, value)

    def copy(self):
        return deepcopy(self)
    
    def compose_sql_insert(self, tablename):
        _subset = {_k: self.copy()[_k] for _k in self.defaults.keys() if self[_k] != self.defaults[_k]}
        if len(_subset) == 0:
            return
        
        for _k in self.primary_keys:
            if _k not in _subset.keys():
                _subset.update({_k: f"nextval('{_k[:2]}seq')"})
        
        for _k in self.foreign_keys:
            if _k not in _subset.keys():
                _subset.update({_k: f"currval('{_k[:2]}seq')"})

        for _k, _v in _subset.items():
            if _v is None:
                _subset.pop(_k)

        sql = f"""
        INSERT INTO {tablename} 
            ({', '.join([_e for _e in _subset.keys()])}) 
        VALUES 
            ({', '.join([str(_e) for _e in _subset.values()])});
        """
        return sql
    
    def compose_sql_update(self, tablename, alterations={}):
        _subset = {_k: _v for _k, _v in alterations.items() if _k in self.defaults.keys()}

        sql = f"""
        UPDATE {tablename} 
        SET ({', '.join([_e for _e in alterations.keys()])}) 
        = ({', '.join([_e for _e in alterations.values()])}) 
        WHERE {' AND '.join([f'{_k} = {self[_k]}' for _k in self.primary_keys])};
        """
        return sql



class ANSSEvent(RestrictedAttribDict):
    primary_keys=['evid','prefor']
    defaults = {
        'evid': "nextval('evseq')",
        'prefor': "nextval('orseq')",
        'prefmag': None,
        'prefmec': None,
        'commid': None,
        'auth': None,
        'subsource': None,
        'etype': 'uk',
        'version': 1,
        'selectflag': 0,
    }
    def __init__(self, **options):
        super().__init__(tablename='event', **options)

    # def __setattr__(self, key, value):
    #     if key == 'orid':
    #         super().__setattr__('prefor', value)
    #     elif key == 'magid':
    #         super().__setattr__('prefmag', value)
    #     elif key == 'mecid':
    #         super().__setattr__('prefmec', value)
    #     else:
    #         super().__setattr__(key, value)

    def get_name(self):
        if self.auth is None and self.etype is None:
            return 'New Event'
        elif self.auth is None:
            return f'New Event ({self.etype})'
        else:
            return f'{self.auth.lower()}{self.evid:d} ({self.etype})'

class ANSSOrigin(RestrictedAttribDict):
    primary_keys=['orid']
    foreign_keys=['evid','prefmag','prefmec']
    defaults = {
        'orid': -999,
        'evid': None,
        'prefmag': None,
        'prefmec': None,
        'commid': None,
        'bogusflag': 1,
        'datetime': 0.,
        'lat': None,
        'lon': None,
        'depth': None,
        'mdepth': None,
        'type': None,
        'algorithm': None,
        'algo_assoc':'Snuffler',
        'auth': None,
        'subsource':'Snuffler',
        'datumhor': None,
        'datumver': None,
        'gap':None,
        'distance':None,
        'wrms':None,
        'stime':None,
        'erhor':None,
        'sdep':None,
        'erlat':None,
        'erlon':None,
        'totalarr':None,
        'totalamp':None,
        'ndef':None,
        'nbs':None,
        'nbfm':None,
        'locevid':None,
        'quality': None,
        'fdepth':'y',
        'fepi':'y',
        'ftime': 'y',
        'vmodelid': None,
        'cmodelid': None,
        'crust_type': None,
        'crust_model': None,
        'gtype': None,
        'rflag': 'a',
    }

    def __init__(self, **options):
        super().__init__(tablename='origin', **options)

    # def __setattr__(self, key, value):
    #     if key == 'prefor':
    #         super().__setattr__('orid', value)
    #     elif key == 'magid':
    #         super().__setattr__('prefmag', value)
    #     elif key == 'mecid':
    #         super().__setattr__('prefmec', value)
    #     else:
    #         super().__setattr__(key, value)

class ANSSAssocaro(RestrictedAttribDict):
    foreign_keys=['orid','arid']
    defaults = {
        'orid': None,
        'arid': None,
        'commid': None,
        'auth': None,
        'subsource': 'Snuffler',
        'iphase': None,
        'importance': None,
        'delta': None,
        'seaz': None,
        'in_wgt': None,
        'wgt': None,
        'timeres': None,
        'ema': None,
        'slow': None,
        'vmodelid': None,
        'scorr': None,
        'sdelay': None,
        'rflag': None,
        'ccset': None,
    }
    def __init__(self, **options):
        super().__init__(tablename='assocaro', **options)

    # def __setattr__(self, key, value):
    #     if key == 'prefor':
    #         super().__setattr__('orid', value)
    #     else:
    #         super().__setattr__(key, value)

class ANSSArrival(RestrictedAttribDict):
    primary_keys=['arid']
    defaults = {
        'arid': None,
        'commid': None,
        'datetime': None,
        'sta': None,
        'net': None,
        'auth': None,
        'subsource': None,
        'channel': None,
        'channelsrc': None,
        'seedchan': None,
        'location': None,
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
        'quality': None,
        'snr': None,
        'rflag': 'a',
    }
    def __init__(self, **options):
        super().__init__(tablename='arrival', **options)

    def get_nslc_ids(self):
        if self.location == '  ':
            _loc = ''
        else:
            _loc = self.location
        if self.seedchan is None and self.channel is not None:
            return ((self.net, self.sta, _loc, self.channel),)
        else:
            return ((self.net, self.sta, _loc, self.seedchan),)
    
    def get_phasename(self):
        return self.iphase
    
    def get_polarity(self):
        
        if self.fm == 'c.':
            return 1
        elif self.fm == 'd.':
            return -1
        elif self.fm == '..':
            return 0
        else:
            return None
        
class ANSSNetmag(RestrictedAttribDict):
    primary_keys=['magid']
    foreign_keys=['orid']
    defaults = {
        'magid': None,
        'orid': None,
        'commid': None,
        'magnitude': None,
        'magtype': None,
        'auth': None,
        'subsource': None,
        'magalgo': None,
        'nsta': None,
        'uncertainty': None,
        'gap': None,
        'distance': None,
        'quality': None,
        'rflag': None,
        'nobs': 0,
    }

    def __init__(self, **options):
        super().__init__(tablename='netmag', **options)

    

class ANSSEventMarker(EventMarker):

    def __init__(self, **options):
        
        
        self._pg_event = ANSSEvent(**options)
        self._pg_origin = ANSSOrigin(**options)
        self._pg_netmag = ANSSNetmag(**options)

        event = Event(
            time=self._pg_origin.datetime,
            lat=self._pg_origin.lat,
            lon=self._pg_origin.lon,
            depth=self._pg_origin.depth,
            magnitude=self._pg_netmag.magnitude,
            magnitude_type=self._pg_netmag.magtype,
            name = self._pg_event.get_name()
        )
        if 'kind' not in options.keys():
            if self._pg_origin.rflag.lower() == 'a':
                kind = 0
            elif self._pg_origin.rflag.lower() == 'c':
                kind = 4
            elif self._pg_origin.rflag.lower() == 'i':
                kind = 3
            elif self._pg_origin.rflag.lower() == 'h':
                kind = 2
            elif self._pg_origin.rflag.lower() == 'f':
                kind = 1
            else:
                kind = 6
        else:
            kind = options['kind']

        super().__init__(
            event=event,
            kind=kind,
            event_hash = event.get_hash()
        )
        self._initial = {'event': self._pg_event.copy(),
                         'origin': self._pg_origin.copy(),
                         'netmag': self._pg_netmag.copy(),
                         'kind': kind}

    def set_kind(self, kind):
        if kind == 1:
            kind = 2
            self._pg_origin.rflag = 'h'
        elif kind == 2:
            self._pg_origin.rflag = 'h' 
        elif kind == 3:
            self._pg_origin.rflag = 'i'
        elif kind == 4:
            self._pg_origin.rflag = 'c'
        elif kind == 5:
            self._pg_origin.rflag = 'a'
        else:
            pass
        super().set_kind(kind)

    def check_for_alterations(self):
        assessment = {}
        # Iterate over underlying data structures that are subject to alteration
        for _k, working in {'event':self._pg_event, 'origin': self._pg_origin, 'netmag': self._pg_netmag, 'kind': self.kind}.items():
            init = self._initial[_k]
            # Compare kind with archived initial kind
            if _k == 'kind':
                if working != init:
                    assessment.update({_k: working})
                else:
                    assessment.update({_k: False})
            else:
                # Iterate over attribute dicts' 
                _sub = {}
                for _s in working.defaults.keys():
                    if working[_s] != init[_s]:
                        _sub.update({_s: working[_s]})
                if _sub == {}:
                    _sub = False
                assessment.update({_k: _sub})
        return assessment

    def compose_sql(self, phase_markers=[]):
        changes = self.check_for_alterations()
        associated = []
        for m in phase_markers:
            if m._event_hash == self._event_hash:
                if not isinstance(m, ANSSPhaseMarker):
                    m = phase2anss(m)
                associated.append(m)
        # If no changes to the event
        if not any(changes.values()):
            # Check for changes on each phase
            # Each not any should return True if no changes are found
            pchanges = [not any(p.check_for_alterations().values()) for p in associated]
            if all(pchanges):
                print(f'No changes to EVID {self._pg_event.evid} and {len(associated)} associated phases')
                new_event = False
                new_arrivals = any(p._pg_arrival.arid is None for p in associated)
                if new_arrivals:
                    new_origin = True
                # If there is a change in total phase count - create new origin
                elif len(associated) != self._pg_origin.totalarr:
                    new_origin = True
                # if there is a change in S-wave phase count - create new origin
                elif sum([p._phasename=='S' for p in associated]) != self._pg_origin.nbs:
                    new_origin = True

            else:
                print(f'No changes to EVID {self._pg_event.evid} but {sum(pchanges)} of {len(associated)} associated phases have alterations')
        
        else:
            print(f'Changes to EVID {self._pg_event.evid}')
            if self._pg_event.evid == ANSSEvent.defaults.evid:
                new_event = True
            else:
                new_event = False

        sql = "BEGIN TRANSACTION;\n"
        # if new_event:
        sql += self._pg_event.compose_sql_insert('event')
        sql += self._pg_origin.compose_sql_insert('origin')
        # sql += self._pg_netmag.compose_sql_insert('netmag')
        for p in associated:
            sql += p._pg_arrival.compose_sql_insert('arrival')
            sql += p._pg_assocaro.compose_sql_insert('assocaro')
        print(sql)

        # elif new_origin:
        #     sql += self._pg_origin.compose_sql_insert()
        #     for p in associated:
        #         if p._pg_arrival.arid is None:
        #             sql += p._pg_arrival.compose_sql_insert()
        #             sql += p._pg_assocaro.compose_sql_insert()
        #         else:
        #             sql += p._pg_arrival.compose_sql_update()
        #             sql += p._pg_assocaro.compose_sql_update()
        # if new_event:
            

        # # If this is a new event
        # if _event.evid == ANSSEvent.defaults.evid:
        #     _event_ttype = 'INSERT INTO event'
        #     _event.evid = "nextval('evseq')"
        #     _event.orid = "nextval('orseq')"
        #     _origin.orid = "currval('orseq')"
        #     _origin.evid = "currval('evseq')"
        
        # # If this is an existing event
        # else:



        # try:
        #     if changes['arrival']['arid'] is None:
        #         arrival_arid_str = "nextval('arseq')"
        #         assocaro_arid_str = "currval('arseq')"
        #     elif isinstance(changes['arrival']['arid'], int):
        #         arrival_arid_str = "%(arid)s"
        #         assocaro_arid_str = "%(arid)s"

                
        # if changes['arrival']:
        #     if 'arid' in changes['arrival'].keys():
        #         if changes['arrival']['']

        # for _k, _v in changes.items():
            



        # return {'event': self._pg_event.get_updated(),
        #         'origin': self._pg_origin.get_updated(),
        #         'netmag': self._pg_netmag.get_updated(),
        #         'kind': self._initial_kind == self.kind}
    



class ANSSPhaseMarker(PhaseMarker):
    def __init__(self, **options):
        self._pg_assocaro = ANSSAssocaro(**options)
        self._pg_arrival = ANSSArrival(**options)
        _ikwargs = {}
        if 'event' in options.keys():
            event = options['event']
            if isinstance(event, Event):
                _ikwargs.update({'event': event,
                                'event_hash': event.get_hash(),
                                'event_time': event.time})
        if 'kind' not in options.keys():
            kind=self.quality2kind()
        else:
            kind = options['kind']

        super().__init__(
            nslc_ids=self._pg_arrival.get_nslc_ids(),
            tmin=self._pg_arrival.datetime,
            tmax=self._pg_arrival.datetime,
            phasename=self._pg_arrival.get_phasename(),
            polarity=self._pg_arrival.get_polarity(),
            automatic=self._pg_arrival.rflag in ['a','A','i','I', None],
            incidence_angle=self._pg_arrival.ema,
            kind=kind,
            **_ikwargs
        )
        ehash = self.get_event_hash()
        # self._initial_event_hash = ehash
        # self._initial_kind = kind
        self._initial = {'assocaro': self._pg_assocaro.copy(),
                         'arrival': self._pg_arrival.copy(),
                         'kind': kind,
                         'event_hash': ehash}

    def check_for_alterations(self):
        self.check_times()
        assessment = {}
        for _k, working in {'assocaro': self._pg_assocaro, 'arrival': self._pg_arrival, 'kind': self.kind, 'event_hash': self.get_event_hash()}.items():
            init = self._initial[_k]
            if _k in ['kind','event_hash']:
                if working != init:
                    assessment.update({_k: working})
                else:
                    assessment.update({_k: False})
            else:
                _sub = {}
                for _s in init.defaults.keys():
                    if working[_s] != init[_s]:
                        _sub.update({_s: working[_s]})
                if _sub == {}:
                    _sub = False
                assessment.update({_k: _sub})
        return assessment


    def quality2kind(self):
        q = self._pg_arrival.quality
        if q is None:
            return 0
        elif q == 1:
            return 1
        elif q in [0.75, 0.8]:
            return 2
        elif q == 0.5:
            return 3
        elif q in [0.3, 0.25]:
            return 4
        elif q == 0:
            return 5
        else:
            return 6

    def set_kind(self, kind):
        super().set_kind(kind)
        if self.kind == 0:
            self._pg_arrival.quality = 0
        elif self.kind == 1:
            self._pg_arrival.quality = 1
        elif self.kind == 2:
            self._pg_arrival.quality = 0.75
        elif self.kind == 3:
            self._pg_arrival.quality = 0.5
        elif self.kind == 4:
            self._pg_arrival.quality = 0.25
        elif self.kind == 5:
            self._pg_arrival.quality == 0
        else:
            pass

        # print(f'Altered quality from {self._initial["arrival"].quality} to {self._pg_arrival.quality}')


    def set_phasename(self, phasename):
        if phasename != self._pg_arrival.iphase:
            self._pg_arrival.iphase = phasename
            self._pg_assocaro.iphase = phasename
        super().set_phasename(phasename)

    def set_polarity(self, polarity):
        if polarity == 1:
            self._pg_arrival.fm='c.'
        elif polarity == -1:
            self._pg_arrival.fm='d.'
        elif polarity == 0:
            self._pg_arrival.fm='..'
        else:
            self._pg_arrival.fm=None
        super().set_polarity(polarity)

    def check_times(self):
        _datetime = 0.5*(self.tmin + self.tmax)
        self._pg_arrival.datetime = _datetime
        if self._pg_arrival.datetime != self._initial['arrival'].datetime:
            self._pg_arrival.arid = None
            self._pg_assocaro.arid = None
        else:
            self._pg_arrival.arid = self._initial['arrival'].arid
            self._pg_assocaro.arid = self._initial['assocaro'].arid
            

    def get_tmin(self):
        self.check_times()
        return super().get_tmin()
    
    def get_tmax(self):
        self.check_times()
        return super().get_tmax()

    # def check_for_alterations(self):

        

    # def get_updated(self):
    #     self.check_times()
    #     return {
    #         'arrival': self._pg_arrival.get_updated(),
    #         'assocaro': self._pg_assocaro.get_update(),
    #         'kind': self._initial_kind == self.kind,
    #         'event_hash': self._initial_event_hash == self._event_hash
    #     }
    

def phase2anss(phasemarker, **options):
    assert isinstance(phasemarker, PhaseMarker)
    datetime = 0.5*(phasemarker.tmin + phasemarker.tmax)
    iphase = phasemarker._phasename
    net, sta, location, channel = phasemarker.one_nslc()
    if location == '':
        location = '  '
    if phasemarker._automatic is None:
        rflag='h'
    elif phasemarker._automatic:
        rflag='a'
    else:
        rflag='i'
    pmark = ANSSPhaseMarker(
        datetime=datetime,
        iphase=iphase,
        net=net,
        sta=sta,
        location=location,
        channel=channel,
        seedchan=channel,
        event=phasemarker._event,
        rflag=rflag,
        ema=phasemarker._incidence_angle,
        **options
    )
    pmark.set_polarity(phasemarker._polarity)
    pmark.set_kind(phasemarker.kind)

    return pmark

def event2anss(eventmarker, **options):
    assert isinstance(eventmarker, EventMarker)
    datetime = eventmarker._event.time
    lon = eventmarker._event.lon
    lat = eventmarker._event.lat
    depth = eventmarker._event.depth
