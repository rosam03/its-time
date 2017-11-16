import requests
import os
import sys
import json
import os.path
import string
import datetime
import yaml


# gets integer value for string month
def month_converter(month):
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    return months[month-1]

# --------------------------------------------------

# checks if year is previous to the present year
def expiried_previous_year(year) :
    return int(year) < int(datetime.date.today().year)

# --------------------------------------------------

# checks if year is the present year
def expiries_this_year(year) :
    return int(year) == int(datetime.date.today().year)

# --------------------------------------------------

# checks if month is the the present month
def expiries_this_month(month) :
    return int(month) == int(datetime.date.today().month)

# --------------------------------------------------

# checks if day is previous to present day
def expiried_previous_day(day) :
    return int(day) < int(datetime.date.today().day)

# --------------------------------------------------

# checks if date is in first 2 weeks of next month
def expiring_next_month(month,day) :
    return (int(month) == int(datetime.date.today().month + 1)) and (int(day) < 15)

# --------------------------------------------------

# parses ssl start date
def get_ssl_start_date(line) :
    # formatted as * start date: MMM DD --:--:-- YYYY  ---
    line = line.split("start date: ")
    line = line[1]
    line = line.split()
    line = line[0]
    line = line.split("-")
    year = line[0]
    month = line[1]
    day = line[2]

    month = str(month)
    if (month[:1] == "0") :
        month = month[1:]
    day = str(day)
    if (day[:1] == "0") :
        day = day[1:]

    return str(year)+"/"+str(month)+"/"+str(day) # or choose own format

# --------------------------------------------------

# parses ssl expiry date
def get_ssl_expiry_date(line,domain) :
    # numbers: 4,3,6 chosen to parse out whitespace/extra chars
    line = line.split("expire date: ")
    line = line[1]
    line = line.split()
    line = line[0]
    line = line.split("-")
    year = line[0]
    month = line[1]
    day = line[2]

    month = str(month)
    if (month[:1] == "0") :
        month = month[1:]
    month = int(month)
    day = str(day)
    if (day[:1] == "0") :
        day = day[1:]
    day = int(day)

    # uncomment to alert in terminal upcoming expiries
    date = " "+str(day)+" "+str(month_converter(month))+" "+str(year)
    alert_expiries(day,month,year,date,domain)

    return str(year)+"/"+str(month)+"/"+str(day)

# --------------------------------------------------

# prints to screen alerts for expired and upcoming ssl certificates
def alert_expiries(day,month,year,date,domain) :
    global records_expired
    global records_coming
    global records_next

    # REPORTS ON RECENTLY EXPIRED OR COMING UP
    # alert on expiries for this month
    if( expiries_this_year(year) ) :
        if( expiries_this_month(month) ) :
            if( expiried_previous_day(day) ) :
                if(domain not in records_expired) :
                        records_expired += domain + "    : expired " + str(datetime.date.today().day-int(day)) + " days ago" + '\n'
            else :
                if (domain not in records_coming):
                        records_coming += domain + "    : is expiring in " + str(int(day)-datetime.date.today().day) + " days" + '\n'
        else : #alert for upcoming month - up to 2 weeks into next month
            if( expiring_next_month(month,day) ) :
                if(datetime.date.today().day >= 20) :
                    if(domain not in records_next) :
                            records_next += domain + "    : is expiring soon on " + date + '\n'
    if( datetime.date.today().year+1 == year) : # if expiring next year
        if( datetime.date.today().month == 12) :  # case for december / end of year to warn on january - expiring_next_month will not work for detecting month in the next year
                if( month == 1 and int(day) < 15 ) :
                    if(domain not in records_next) :
                            records_next += domain + "    : is expiring soon on " + date + '\n'

# --------------------------------------------------

# iterates through file with unparsed ssl dates and initiates file writing
def parse_ssl(inFile) :
    global FOUND_SITE
    global SSL_START
    global SSL_END
    global GOT_SSL

    for line in inFile:

        if(not FOUND_SITE) : # didnt reach new domain record yet
            domain = obtain_domain(line)

        if(FOUND_SITE) : # domain record has been found

              if(not GOT_SSL) : # ssl has yet to be found
                    obtain_ssl(line,domain)

                    # both ssl dates have been obtained
                    if(SSL_END and SSL_START) :
                          GOT_SSL = True
                          FOUND_SITE = False # prepare to find new domain record

                    exitLineStr = "done partial search"

                    # if ssl was not obtained  - prepare for new domain
                    if( not GOT_SSL and exitLineStr in line ) :
                          FOUND_SITE = False
                          GOT_SSL = True

# --------------------------------------------------

# determines whether the given line in file is a domain
def obtain_domain(line) :
    global FOUND_SITE
    global SSL_START
    global SSL_END
    global GOT_SSL

    if("," in line) :
        # domain record found - reset flags
        FOUND_SITE = True
        GOT_SSL = False
        SSL_START = False
        SSL_END = False

        domain = line.strip() # remove trailing new line
        domain = domain.replace(",","") # remove comma (indicated that this is domain)
        return domain # parse out comma

# --------------------------------------------------

# determines whether the given line in file is an ssl start or expiry date
def obtain_ssl(line,domain) :
    global SSL_START
    global SSL_END

    sslStartStr = "start date:"
    sslEndStr = "expire date:"

    # parse ssl start date
    if( not SSL_START and sslStartStr in line ) :
        value = get_ssl_start_date(line)
        SSL_START = True

    # parse ssl expiry date
    if( not SSL_END and sslEndStr in line ) :
        value = get_ssl_expiry_date(line,domain)
        SSL_END = True

# --------------------------------------------------

# open files
def prepare_files() :

    with open(CFG, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    SSL_PATH = config['ssl_dates_file']

    try:
            inFile = open(SSL_PATH, "rt") # this will contain domains and output of openssl
            return inFile
            pass
    except IOError:
            print ("Unable to open " + SSL_PATH + " file") #Does not exist OR no read permissions
            sys.exit()

# --------------------------------------------------

# closes input and output files and removes files w/ sensitive info from servers
def close_files(inFile) :

    with open(CFG, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    SSL_PATH = config['ssl_dates_file']
    DOMAIN_PATH = config['domain_list_file']

    inFile.close()

    try:
        os.system("rm " + SSL_PATH) # remove to delete ssl dates from server
        os.system("rm " + DOMAIN_PATH ) # remove to delete domain list from server
    except:
        print ("Unable to remove files: " + SSL_PATH + " and " + DOMAIN_PATH)

# --------------------------------------------------

def slackMessage(token, channel, name, text, attachments=""):
  url = 'https://slack.com/api/chat.postMessage'
  try:
      r = requests.post(url, data={'token': token, 'channel': channel, 'username': name, 'as_user': 'true', 'text': text, 'attachments': attachments})
  except:
      print ("Failure: Could not post to Slack.")

# --------------------------------------------------

def main() :

    global records_expired
    global records_coming
    global records_next
    records_expired = ''
    records_coming = ''
    records_next = ''

    # flags for determining state of program
    global FOUND_SITE
    global SSL_START
    global SSL_END
    global GOT_SSL

    FOUND_SITE = False
    GOT_URL = False
    SSL_START = False
    SSL_END = False
    GOT_SSL = False

    with open(CFG, 'r') as ymlfile:
        config = yaml.load(ymlfile)

    SSL_PATH= config['ssl_dates_file']

    inFile = prepare_files()
    parse_ssl(inFile)

    close_files(inFile)

    SLACK_TOKEN = config['slack_token']
    SLACK_CHANNEL = config['slack_channel']
    SLACK_NAME = config['slack_username']
    SLACK_ATTACHMENT_TITLE = config['slack_attachment_title']
    SLACK_ATTACHMENT_VALUE = config['slack_attachment_value']

    SLACK_TEXT = config['slack_text'] + '\n' + records_coming + '\n' + records_next + '\n' + records_expired

    if (not records_expired and not records_coming and not records_next) :
        print ("No SSL certificate expiries to show.")
    else :
        attachments = json.dumps([{'fields': [{'title': SLACK_ATTACHMENT_TITLE,'value': SLACK_ATTACHMENT_VALUE,'short': 'false'}]}])
        slackMessage(SLACK_TOKEN, SLACK_CHANNEL, SLACK_NAME, SLACK_TEXT, attachments)

# --------------------------------------------------

CFG = 'config.yaml'

main()
