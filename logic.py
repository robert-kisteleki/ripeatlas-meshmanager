import urllib
import urllib2
import json
import mechanize
import traceback

from django.core.cache import cache

from meshmgr.settings import PROBE_API, MSM_API, PARTICIPATION_API
from meshmgr.settings_private import PARTICIPATION_API_KEY, MSM_API_KEY, MSM_STOP_API_KEY


HTTP_TIMEOUT = 20


def get_probe_data_from_api(param_list):
    param_list += ['limit=100']
    params = '&'.join(param_list)
    f = urllib.urlopen(PROBE_API+'?'+params)
    res = f.read()
    f.close()

    probes = json.loads(res)
    probe_list = []
    for probe in probes['objects']:
        probe_list.append(probe['id'])
        set_probe_data(probe['id'], probe)

    return probe_list


def set_probe_data(probe_id, probe_data):
    cache.set('prb'+str(probe_id), probe_data, None)


def get_probe_data(probe_id):
    probe_data = cache.get('prb'+str(probe_id))
    if probe_data is None:
        #print('WARNING: cache miss on %d' % probe_id)
        get_probe_data_from_api([('id=%d' % probe_id)])
        return cache.get('prb'+str(probe_id))
    else:
        return probe_data


def make_measurement(probe_id, af, target, probe_list, descr):

    # sanity check + this may actually happen for a single probe mesh
    if len(probe_list) == 0:
        print('No probes to measure %s' % descr)
        return

    print('Need to schedule v%d msm against %s called "%s" using probes %s' % (af, probe_id, descr, probe_list))

    to_post = '''{
    "definitions": [
        {
            "target": "%s",
            "description": "%s",
            "type": "traceroute",
            "protocol": "ICMP",
            "af": %d,
            "interval": 3600
        }
    ],
    "probes": [
        {
            "requested": %d,
            "type": "probes",
            "value": "%s"
        }
    ]
}''' % (target, descr, af, len(probe_list), ','.join(map(str, probe_list)))

    post_url = MSM_API + '?key=' + MSM_API_KEY
    #print( 'POSTing to %s: %s' % (post_url, to_post))

    req = mechanize.Request(
        post_url,
        data=to_post,
        headers={
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
    )
    try:
        br = mechanize.Browser()
        resp = br.open(req, timeout=HTTP_TIMEOUT)
    except mechanize.HTTPError, response:
        print('Failed to create measurement: %s (%s)' % (response, response.read()))
        return
    except:
        print('Failed to get URL: %s', traceback.format_exc())
        return

    response_data = resp.read()
    try:
        msm_id = json.loads(response_data)['measurements'][0]
    except:
        print('Failed to create measurement: %s' % response_data)
        return

    print('Measurement ID: %d' % msm_id)
    return msm_id

def stop_measurement(msm_id):
    stop_url = "%s/%d/?key=%s" % ( MSM_API, msm_id, MSM_STOP_API_KEY )
    print "stopping via: %s" % ( stop_url )
    req = urllib2.Request(stop_url)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Accept', 'application/json')
    req.get_method = lambda: 'DELETE'
    try:
        response = urllib2.urlopen(req)
    except:
        print('Failed to stop measurement: %s' % (msm_id) )
        return

def check_probe_involvement(msm_id, current_probes_list):

    #print('Checking probe involvement in msm %d' % msm_id)

    f = urllib.urlopen(MSM_API+'?fields=probes&msm_id='+str(msm_id))
    res = f.read()
    f.close()

    result = json.loads(res)
    if result['meta']['total_count'] != 1:
        return 0

    msm_probes_list = []
    for probe in result['objects'][0]['probes']:
        msm_probes_list.append(probe['id'])

    new_probes_list = list(set(current_probes_list)-set(msm_probes_list))

    """
    print 'current: ', current_probes_list
    print 'msm: ', msm_probes_list
    print 'new: ', new_probes_list
    """

    if len(new_probes_list) == 0:
        return 0

    for new_probe_id in new_probes_list:
        print('Need to add probe %d to msm %d' % (new_probe_id, msm_id))

        to_post = '''{
    "msm_id": %d,
    "probes": [
        {
            "action": "add",
            "requested": 1,
            "type": "probes",
            "value": "%d"
        }
    ]
}''' % (msm_id, new_probe_id)

        post_url = PARTICIPATION_API + '?key=' + PARTICIPATION_API_KEY
        #print( 'POSTing to %s: %s' % (port_url, to_post))

        req = mechanize.Request(
            post_url,
            data=to_post,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        )
        try:
            br = mechanize.Browser()
            resp = br.open(req, timeout=HTTP_TIMEOUT)
        except mechanize.HTTPError, response:
            print('Failed to add probe %s to measurement %d because: %s (%s)' %
                  (new_probe_id, msm_id, response, response.read())
            )
            return
        except:
            print('Failed to get URL: %s', traceback.format_exc())
            return

        response_data = resp.read()
        try:
            # this is not used so there's no point in doing it
            partic_id = json.loads(response_data)['requests'][0]
        except:
            print('Failed to add probe %s to measurement %d because: %s' % (new_probe_id, msm_id, response_data))
            return
        print('Response: %s' % response_data)

    return len(new_probes_list)
