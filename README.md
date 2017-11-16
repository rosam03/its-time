# its-time

Keep your sites up to date.
Using a list of domains, find out which ones have SSL certificates that are expiring soon.
Results can be seen via command-line or printed in a Slack channel of your choosing.

## requirements

* Python 2.7+
* Platform: Unix/Linux/MacOS (for the file loop in chron)
* Libraries: requests, json, datetime, yaml (acquire using `pip install`)
* OpenSSL command-line tool
* Network connection

## Configuration
* File to edit: `config.yaml`

* Fields to include:
```yaml

  ssl_dates_file: 'output.txt'
  slack_token:
  slack_channel:
  slack_username:
  slack_text: SSL certificates report
  slack_attachment_value:
  slack_attachment_title:
```

* Notes:
 - The config file should be named ```config.yaml``` in order to be readable by the default scripts.
 - To edit where the scripts read this file from, edit the CONFIG variable containing the filename at the bottom of the script before main() is called.

=====

## slack integration

To display the results in a Slack channel, see their api bot documentation to obtain an authorization token. For this script, you will need a username with a corresponding token and a channel to write to. Insert these values into the config.yaml file. If you want to change the text and value fields, modify them in the config.yaml file too.

If you don't want to use the Slack integration, comment out
'slackMessage(SLACK_TOKEN, SLACK_CHANNEL, SLACK_NAME, SLACK_TEXT, attachments)'
in the else statement in main() with the default config.yaml values. Alternatively, you can erase the functions and dependencies (config.yaml, slackMessage(), main()).

## set up

1) Put the file with a list of domains (separated by a new line) in the parent directory

Warning: The file names we use are domains.txt and output.txt, if they exist prior to running the program, they will be deleted. To change the file names used, go to the chron file and modify all file calls in the command containing 'cat domains.txt | while '.

Ensure the file names you use correspond to those in the config.yaml file:
config['ssl_dates_file'] is the output file containing the domains and ssl dates (originally output.txt)

2) Run the bash script -> ./chron

* What happens?
 - Iterates through the list of domains generated in the loop in the bash script, collects SSL certificate details, and writes to output.txt which will then be used in certs_expiring.py
 - The openssl command exhausts connecting to all SSL/TLS versions as some sites may not support the default version of TLS/SSL that cURL uses. To ensure we are retreieving SSL certificate details for all sites, we must perform this exhaustive command.

## automate it

This script was originally used for automation with the Slack integration, if you are making use of the Slack integration here, you can run the chron file as a chron job. See your operating system requirements for scheduling a chron job.

## time
Duration for approx. 1000 domains:
 - 62 minutes
