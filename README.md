# RIPE Atlas MeshManager

A simple application to manage traceroute meshes with RIPE Atlas.

## How to use it

The app is in the form of a Django application. It's known to work with Django 1.6

## Changelog

* v0.3 - 2014-10-14
    * incorporated Emile's patch to stop adhoc measurements
    * added some URLs to give access to list of meshes and details

* v0.2 - 2014-09-10
    * added -d to update_meshes command
    * added --details to list_meshes
    * minor model changes

* v0.1 - 2014-08-22
    * does country + ad hoc meshes
    * ad-hoc meshes don't support delete or remove
    * there's no measurement rescheduling when a probe changes IPs
