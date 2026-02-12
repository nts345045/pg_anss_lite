from pyrocko.gui.snuffler.marker import PhaseMarker, EventMarker
from pyrocko.model.event import Event
from pyrocko.model.station import Station
from obspy.core.util.attribdict import AttribDict
from obspy import UTCDateTime
from warnings import WarningMessage

class RestrictedAttribDict(AttribDict):
    primary_keys = ()
    def __init__(self, tablename, **options):
        super().__init__({_k:_v for _k, _v in options.items()})
        self.tablename=tablename
        self._initial = AttribDict({_k:_v for _k, _v in self.copy().items()})

    def __setattr__(self, key, value):
        if key in self.defaults.keys():
            super().__setattr__(key, value)
        elif key == 'primary_key':
            raise AttributeError(f'Cannot alter the primary_keys attribute after initialization')
        else:
            return
    
    def get_updated(self):
        output = {}
        for _k, _v in self.items():
            if self._initial[_k] != _v:
                output.update({_k:_v})
        if len(output) > 0:
            return output
        else:
            return False


class ANSSEvent(RestrictedAttribDict):
    indices=('evid')
    defaults = {
        'evid': -999,
        'prefor': None,
        'prefmag': None,
        'prefmec': None,
        'commid': None,
        'auth': None,
        'subsource': None,
        'etype': 'uk',
        'version': 1,
        'selectflag': 0,
        'lddate': UTCDateTime()
    }
    def __init__(self, **options):
        super().__init__(tablename='event', **options)

    def __setattr__(self, key, value):
        if key == 'orid':
            super().__setattr__('prefor', value)
        elif key == 'magid':
            super().__setattr__('prefmag', value)
        elif key == 'mecid':
            super().__setattr__('prefmec', value)
        else:
            super().__setattr__(key, value)

    def get_name(self):
        if self.auth is None and self.etype is None:
            return 'New Event'
        elif self.auth is None:
            return f'New Event ({self.etype})'
        else:
            return f'{self.auth.lower()}{self.evid:d} ({self.etype})'

class ANSSOrigin(RestrictedAttribDict):
    indices=('orid')
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
        'lddate': UTCDateTime()
    }

    def __init__(self, **options):
        super().__init__(tablename='origin', **options)

    def __setattr__(self, key, value):
        if key == 'prefor':
            super().__setattr__('orid', value)
        elif key == 'magid':
            super().__setattr__('prefmag', value)
        elif key == 'mecid':
            super().__setattr__('prefmec', value)
        else:
            super().__setattr__(key, value)

class ANSSAssocaro(RestrictedAttribDict):
    indices=('orid','arid')
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
        'lddate': UTCDateTime()
    }
    def __init__(self, **options):
        super().__init__(tablename='assocaro', **options)

    def __setattr__(self, key, value):
        if key == 'prefor':
            super().__setattr__('orid', value)
        else:
            super().__setattr__(key, value)

class ANSSArrival(RestrictedAttribDict):
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
        'qulity': None,
        'snr': None,
        'rflag': 'a',
        'lddate': UTCDateTime()
    }


class ANSSNetmag(RestrictedAttribDict):
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
        'lddate': None
    }

    def __init__(self, **options):
        super().__init__(tablename='netmag', **options)

    def get_nslc_ids(self):
        if self.location == '  ':
            _loc = ''
        else:
            _loc = self.location
        if self.seedchan is None and self.channel is not None:
            return ((self.net, self.sta, _loc, self.channel))
        else:
            return ((self.net, self.sta, _loc, self.seedchan))

class ANSSEventMarker(EventMarker):

    def __init__(self, **options):
        self._pg_event = ANSSEvent(**options)
        self._pg_origin = ANSSOrigin(**options)
        self._pg_netmag = ANSSNetmag(**options)
        event = Event(
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
        self._initial_kind = kind


    def get_updated(self):
        return {'event': self._pg_event.get_updated(),
                'origin': self._pg_origin.get_updated(),
                'netmag': self._pg_netmag.get_updated(),
                'kind': self._initial_kind == self.kind}
    
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
        self._initial_kind = kind

        super().__init__(
            nslc_ids=self._pg_arrival.get_nslc_ids(),
            tmin=self._pg_arrival.datetime,
            tmax=self._pg_arrival.datetime,
            phasename=self._pg_arrival.get_phasename(),
            polarity=self._pg_arrival.get_polarity(),
            automatic=self._pg_arrival.rflag in ['a','A','i','I', None],
            incidence_angle=self._pg_arrival.ema,
            kind=kind
            **_ikwargs
        )

        self._initial_event_hash = self._event_hash.copy()

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
        if kind == 0:
            self._pg_arrival.quality = 0
        elif kind == 1:
            self._pg_arrival.quality = 1
        elif kind == 2:
            self._pg_arrival.quality = 0.75
        elif kind == 3:
            self._pg_arrival.quality = 0.5
        elif kind == 4:
            self._pg_arrival.quality = 0.25
        elif kind == 5:
            self._pg_arrival.quality == 0
        else:
            pass


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
        if self._pg_arrival.datetime != self._pg_arrival._initial.datetime:
            self._pg_arrival.arid = None
            self._pg_assocaro.arid = None
        else:
            self._pg_arrival.arid = self._pg_arrival._initial.arid
            self._pg_assocaro.arid = self._pg_assocaro._initial.arid
            

    def get_tmin(self):
        self.check_times()
        return super().get_tmin()
    
    def get_tmax(self):
        self.check_times()
        return super().get_tmax()

    def get_updated(self):
        self.check_times()
        return {
            'arrival': self._pg_arrival.get_updated(),
            'assocaro': self._pg_assocaro.get_update(),
            'kind': self._initial_kind == self.kind,
            'event_hash': self._initial_event_hash == self._event_hash
        }
    

def phase2anss(phasemarker, **options):
    assert isinstance(phasemarker, PhaseMarker)
    datetime = 0.5*(phasemarker.tmin + phasemarker.tmax)
    iphase = phasemarker.phasename
    net, sta, location, channel = phasemarker.one_nslc()
    if location == '':
        location = '  '
    if phasemarker.automatic is None:
        rflag='h'
    elif phasemarker.automatic:
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




    # def __setattr__(self, key, value):
    #     if key == 'evid':
    #         try:
    #             value = int(value)
    #             if value < 1:
    #                 raise ValueError(f'Only default value for EVID can be non-positive')
    #         except:
    #             raise TypeError(f'evid values must be int-like')
    #     if key in ['prefor','prefmag','prefmec']:
    #         try:
    #             value = int(value)
    #         except:
    #             value = None
    #     if key == 'etype':
    #         if isinstance(value, str):
    #             if len(value) == 2:
    #                 value = value.lower()
    #             else:
    #                 raise ValueError('etype must be a 2-character string')
    #         else:
    #             value='uk'
    #     if key in ['version','selectflag']:
    #         try:
    #             value = int(value)
    #             if value < 0:
    #                 raise ValueError(f'{key} must be non-negative')
    #             elif key == 'selectflag' and value > 1:
    #                 raise ValueError('selectflag must be either 0 or 1')
    #         except:
    #             raise TypeError(f'{key} must be int-like')