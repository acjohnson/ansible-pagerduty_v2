#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
import json
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url
from pagerduty_v2 import api as pagerduty


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''

module: pagerduty_v2
short_description: PagerDuty integration for Ansible
description:
    - This module will let you integrate your workflows, releases, deployments, etc with your PagerDuty account!
version_added: "2.4"
author:
    - "Aaron Johnson"
requirements:
    - PagerDuty API v2 key

'''


def check_incident(api_key, incident_id, incident_status):
    """
    Checks incident status

    :param api_key: PagerDuty API v2 key
    :type  api_key: str
    :param incident_id: unique incident id or incident number
    :type  incident_id: str
    :param incident_status: triggered, acknowledged, or resolved
    :type  incident_status: str

    :return: JSON and boolean
    :rtype:  tuple
    """

    if incident_id:
        data = {
            "api_key": api_key,
            "incidents": {
                "id": incident_id
            }
        }

        result = pagerduty.v2(**data)

        if 'incident' in result:
            incident = result.get('incident')
            if incident_status != incident.get('status'):
                return incident, True
            return incident, False

        return result, False
    else:
        return {"Response": "incident_id was not specified, triggering new incident!"}, True


def create_incident(api_key,
                    email,
                    service_id,
                    escalation_policy_id,
                    incident_title,
                    incident_priority_id,
                    incident_details):
    """
    Creates incidents with status 'triggered'

    :param api_key: PagerDuty API v2 key
    :type  api_key: str
    :param email: valid email address associated with PagerDuty account
    :type  email: str
    :param service_id: on the Services page, in the URL, the last set of characters after the / is the service ID
    :type  service_id: str
    :param escalation_policy_id: escalation policy id to associate with the incident
    :type  escalation_policy_id: str
    :param incident_title: title or name of the incident to create
    :type  incident_title: str
    :param incident_priority_id: priority of this incident
    :type  incident_priority_id: str
    :param incident_details: body of the incident message
    :type  incident_details: str

    :return: JSON and boolean
    :rtype:  tuple
    """

    data = {
        "api_key": api_key,
        "email": email,
        "service_id": service_id,
        "escalation_policy_id": escalation_policy_id,
        "incidents": {
            "title": incident_title,
            "status": "triggered",
            "details": incident_details,
            "priority_id": incident_priority_id
        }
    }

    result = pagerduty.v2(**data)

    if 'incident' in result:
        incident = result.get('incident')
        return incident, True

    return result, False


def update_incident(api_key,
                    email,
                    incident_id,
                    incident_status):
    """
    Updates incident status

    :param api_key: PagerDuty API v2 key
    :type  api_key: str
    :param email: valid email address associated with PagerDuty account
    :param email: str
    :param incident_id: unique incident id or incident number
    :type  incident_id: str
    :param incident_status: triggered, acknowledged, or resolved
    :type  incident_status: str

    :return: JSON and boolean
    :rtype:  tuple
    """

    data = {
        "api_key": api_key,
        "email": email,
        "incidents": {
            "id": incident_id,
            "status": incident_status
        }
    }

    result = pagerduty.v2(**data)

    if 'incident' in result:
        incident = result.get('incident')
        return incident, True

    return result, False


def start_maintenance_window(api_key,
                             email,
                             service_id,
                             maintenance_window_description,
                             maintenance_window_start_time,
                             maintenance_window_duration,
                             maintenance_window_timezone):

    """
    Starts maintenance windows in your timezone

    :param api_key: PagerDuty API v2 key
    :type  api_key: str
    :param email: valid email address associated with PagerDuty account
    :type  email: str
    :param service_id: on the Services page, in the URL, the last set of characters after the / is the service ID
    :type  service_id: str
    :param maintenance_window_description: description of maintenance
    :type  maintenance_window_description: str
    :param maintenance_window_start_time: timestamp or 'now' for start of maintenance window
    :type  maintenance_window_start_time: str
    :param maintenance_window_duration: number of hours the maintenance window will remain open unless manually closed
    :type  maintenance_window_duration: str
    :param maintenance_window_timezone: timezone used for maintenance window start timestamp
    :type  maintenance_window_timezone: str

    :return: JSON and boolean
    :rtype:  tuple
    """

    data = {
        "api_key": api_key,
        "email": email,
        "service_id": service_id,
        "maintenance_windows": {
            "description": maintenance_window_description,
            "start_time": maintenance_window_start_time,
            "duration": maintenance_window_duration,
            "action": "start",
            "timezone": maintenance_window_timezone
        }
    }

    result = pagerduty.v2(**data)

    if 'maintenance_window' in result:
        maintenance_window = result.get('maintenance_window')
        return maintenance_window, True

    return result, False


def stop_maintenance_window(api_key,
                            service_id,
                            maintenance_window_id):
    """
    Stops maintenance windows

    :param api_key: PagerDuty API v2 key
    :type  api_key: str
    :param service_id: on the Services page, in the URL, the last set of characters after the / is the service ID
    :type  service_id: str
    :param maintenance_window_id: maintenance window id to stop
    :type  maintenance_window_id: str

    :return: JSON and boolean
    :rtype:  tuple
    """

    data = {
        "api_key": api_key,
        "service_id": service_id,
        "maintenance_windows": {
            "id": maintenance_window_id,
            "action": "stop",
        }
    }

    result = pagerduty.v2(**data)

    if 'maintenance_window' in result:
        maintenance_window = result.get('maintenance_window')
        return maintenance_window, True

    return result, False


def main():

    module = AnsibleModule(
        argument_spec=dict(
            api_key=dict(required=True),
            service_id=dict(required=False, default=None),
            email=dict(required=False, default=None),
            escalation_policy_id=dict(required=False, default=None),
            request_type=dict(required=True, choices=['incidents', 'maintenance_windows']),
            incident_title=dict(required=False, default=None),
            incident_details=dict(required=False, default='Incident Created via Ansible'),
            incident_priority_id=dict(required=False, default=None),
            incident_id=dict(required=False, default=None),
            incident_status=dict(required=False, choices=['triggered', 'acknowledged', 'resolved']),
            maintenance_window_description=dict(required=False, default='Maintenance Window Created via Ansible'),
            maintenance_window_start_time=dict(required=False, default='now'),
            maintenance_window_duration=dict(required=False, default='1'),
            maintenance_window_timezone=dict(required=False, default='US/Central'),
            maintenance_window_id=dict(required=False, default=None),
            maintenance_window_action=dict(required=False, choices=['start', 'stop'])
        ),
        supports_check_mode=True
    )

    api_key = module.params.get('api_key')
    service_id = module.params.get('service_id')
    email = module.params.get('email')
    escalation_policy_id = module.params.get('escalation_policy_id')
    request_type = module.params.get('request_type')

    incident_title = module.params.get('incident_title')
    incident_details = module.params.get('incident_details')
    incident_priority_id = module.params.get('incident_priority_id')
    incident_id = module.params.get('incident_id')
    incident_status = module.params.get('incident_status')

    maintenance_window_description = module.params.get('maintenance_window_description')
    maintenance_window_start_time = module.params.get('maintenance_window_start_time')
    maintenance_window_duration = module.params.get('maintenance_window_duration')
    maintenance_window_timezone = module.params.get('maintenance_window_timezone')
    maintenance_window_id = module.params.get('maintenance_window_id')
    maintenance_window_action = module.params.get('maintenance_window_action')

    #
    # Process incident requests
    #
    if 'incidents' in request_type:
        if 'triggered' not in incident_status and incident_id is None:
            module.fail_json(msg="incident_id is required for "
                                 "acknowledged or resolved status")

        if 'triggered' in incident_status:
            for arg in ['incident_title', 'service_id', 'email']:
                if module.params.get(arg) is None:
                    module.fail_json(msg="{0} is required for "
                                         "creating triggered incidents".format(arg))

        out, changed = check_incident(api_key, incident_id, incident_status)

        if not module.check_mode and changed is True:
            if 'triggered' in incident_status:
                out, changed = create_incident(api_key,
                                               email,
                                               service_id,
                                               escalation_policy_id,
                                               incident_title,
                                               incident_priority_id,
                                               incident_details)
            else:
                out, changed = update_incident(api_key,
                                               email,
                                               incident_id,
                                               incident_status)

    #
    # Process maintenance window requests
    #
    if 'maintenance_windows' in request_type:
        for arg in ['service_id', 'maintenance_window_action']:
            if module.params.get(arg) is None:
                module.fail_json(msg="{0} is required for "
                                     "starting or stopping maintenance windows".format(arg))

        if 'start' in maintenance_window_action:
            if email is None:
                module.fail_json(msg="email is required for "
                                     "starting maintenance windows")
            if not module.check_mode:
                out, changed = start_maintenance_window(api_key,
                                                        email,
                                                        service_id,
                                                        maintenance_window_description,
                                                        maintenance_window_start_time,
                                                        maintenance_window_duration,
                                                        maintenance_window_timezone)

        if 'stop' in maintenance_window_action:
            if maintenance_window_id is None:
                module.fail_json(msg="maintenance_window_id is required for "
                                     "stopping maintenance windows")

            if not module.check_mode:
                out, changed = stop_maintenance_window(api_key,
                                                       service_id,
                                                       maintenance_window_id)

    if 'id' in out:
        module.exit_json(result=out, changed=changed, id=out.get('id'))
    else:
        module.exit_json(result=out, changed=changed)


if __name__ == '__main__':
    main()
