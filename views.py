from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.db import connection
from django.template import RequestContext
from django.http import HttpResponse, Http404

import json

from meshmgr.models import CountryMesh, AdhocMesh, MeshMember


def list_meshes(request):
    data = []
    for mesh in CountryMesh.objects.all():
        meshdata = {
            'type': 'country',
            'enabled' : mesh.enabled,
            'id': mesh.pk,
            'cc' : mesh.iso3166,
            'country' : mesh.country_name
        }
        data.append(meshdata)

    for mesh in AdhocMesh.objects.all():
        meshdata = {
            'type': 'ad-hoc',
            'enabled' : mesh.enabled,
            'id': mesh.pk,
            'descr' : mesh.descr
        }
        data.append(meshdata)

    return HttpResponse(
        json.dumps( data, indent=2 ),
        content_type="application/json"
    )


def list_members(request):
    try:
        mesh_id = int(request.GET.get('mesh_id'))
    except:
        return HttpResponse("Please provide a mesh_id")

    data = []
    for member in MeshMember.objects.filter(mesh=mesh_id):
        member_data = {
            'probe_id' : member.prb_id,
            'added' : time_convert(member.prb_added),
            'last_public' : member.prb_last_public,
            'last_status' : member.prb_last_status,
            'msm4_id' : member.msm4_id,
            'msm4_added' : time_convert(member.msm4_added),
            'msm6_id' : member.msm6_id,
            'msm6_added' : time_convert(member.msm6_added),
        }
        if member.prb_last_public:
            member_data['last_ipv4'] = member.prb_last_ipv4
            member_data['last_ipv6'] = member.prb_last_ipv6
        data.append(member_data)

    return HttpResponse(
        json.dumps( data, indent=2 ),
        content_type="application/json"
    )

def time_convert(t):
    if not t:
        return None
    else:
        return t.strftime('%s')
