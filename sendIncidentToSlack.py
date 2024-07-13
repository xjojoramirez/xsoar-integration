from datetime import datetime, timedelta

#get today - 7days
def get_date_7_days_ago():
    today = datetime.utcnow()
    seven_days_ago = today - timedelta(days=7)
    return seven_days_ago.strftime('%Y-%m-%dT%H:%M:%SZ')

#query get incidents(severity: high and date 7days ago)
def get_filtered_incidents():
    date_7_days_ago = get_date_7_days_ago()
    query = f'severity:high AND created:<="{date_7_days_ago}"'
    
    #from !getIncidents command
    res = demisto.executeCommand('getIncidents', {'query': query})

    if isError(res[0]):
        return_error(f'Failed to retrieve incidents: {get_error(res)}')

    incidents_data = res[0]['Contents']['data']
    if incidents_data is None:
        return []

    return incidents_data

#send to slack function
def send_incident_to_slack(incident):
    channel = '#bot-updates'  # slack channel
    message = (f"Incident Name: {incident.get('Name')}\n"
            f"Incident Severity: {incident.get('Severity')}\n"
            f"Incident Created: {incident.get('Created')}")

    #from !send-notification command
    res = demisto.executeCommand('send-notification', {
        'message': message,
        'channel': channel
    })

    if isError(res[0]):
        return f"Failed to send incident '{incident.get('Name')}' to Slack."
    else:
        return f"Successfully sent incident '{incident.get('Name')}' to Slack."

#main execute
def main():
    try:
        incidents = get_filtered_incidents()
        if not incidents:
            return_results('No incidents found.')
            return

        slack_results = []
        for incident in incidents:
            incident_info = {
                'Name': incident.get('name'),
                'Severity': incident.get('severity'),
                'Created': incident.get('created')
            }

            slack_result = send_incident_to_slack(incident_info)
            slack_results.append(slack_result)

        return_results(slack_results)

    except Exception as e:
        return_error(f'Error occurred: {str(e)}')

if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
