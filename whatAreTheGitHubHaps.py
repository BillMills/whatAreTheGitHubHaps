from datetime import datetime
from dateutil.parser import parse
import pytz
import requests
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import dates
from matplotlib import patches
import webbrowser

# (user, pass)
auth = ('kittens', 'rainbows')

def genericFetch(target, cutoff, route):
    '''
    a generic fetch of the named '/route', from target repo 'owner/repo', going back in time to at least cutoff, a datetime object.
    '''

    if route.find('?') == -1:
        route += '?page='
    else:
        route += '&page='
    result = requests.get("https://api.github.com/repos/"+target+route+'1', auth=auth).json()
    page = 2
    
    while (len(result)>0) and (parse(result[-1]['created_at']) > cutoff):
        r = requests.get("https://api.github.com/repos/"+target+route+str(page), auth=auth).json()
        if len(r) == 0:
            break
        result = result + r
        page += 1

    return result


def fetchPulls(target, cutoff):
    '''
    fetch the pull requests for target, a string like 'owner/repo'
    '''

    return genericFetch(target, cutoff, "/pulls?state=all")

def fetchComments(target, cutoff):
    '''
    fetch the comments for target, a string like 'owner/repo'
    '''

    return genericFetch(target, cutoff, "/issues/comments")


def fetchIssues(target, cutoff):
    '''
    fetch the issues for target, a string like 'owner/repo'
    '''

    return genericFetch(target, cutoff, "/issues?state=all")


def fetchNonPRissues(target, cutoff):
    '''
    fetch the non-PR issues for target, a string like 'owner/repo'
    '''

    issues = []
    r = genericFetch(target, cutoff, "/issues?state=all")

    for issue in r:
        if 'pull_request' in issue:
            pass
        else:
            issues.append(issue)

    return issues    

def submittedPulls(pulls):
    '''
    take the json returned from fetchPulls, and return only those pulls with state='open', in the same format.
    '''

    subs = []
    for pull in pulls:
        if pull['state'] == 'open':
            subs.append(pull)

    return subs

def mergedPulls(pulls):
    '''
    take the json returned from fetchPulls, and return only those pulls with state='closed' & merged_at != None, 
    in the same format.
    '''

    merged = []
    for pull in pulls:
        if pull['state'] == 'closed' and pull['merged_at'] is not None:
            merged.append(pull)

    return merged

def rejectedPulls(pulls):
    '''
    take the json returned from fetchPulls, and return only those pulls with state='closed' & merged_at == None, 
    in the same format.
    '''

    rejected = []
    for pull in pulls:
        if pull['state'] == 'closed' and pull['merged_at'] is None:
            rejected.append(pull)

    return rejected

def pullTimes(pulls):
    '''
    take the json returned from fetchPulls et al, and extract a list of PR times as datetime objects
    '''

    pulltimes = []
    for pull in pulls:
        time = pull['created_at']
        dt = processTime(time)
        pulltimes.append(dt.date())

    return pulltimes

def processTime(timeString):
    '''
    turn a github time string into a datetime object
    '''

    return datetime.strptime(timeString, '%Y-%m-%dT%H:%M:%SZ')


def trimTimes(times, min, max):
    '''
    take a list times of datetime objects, remove times outside [min, max], and return the resulting list
    '''

    result = []
    for time in times:
        if time >= min and time <= max:
            result.append(time)

    return result

def tidyTime(pulls, min, max):
    '''
    take a list of lists of pulls, and return a list of times trimmed for min, max 
    '''
    times = pullTimes(pulls)

    times = trimTimes(times, min, max)

    return times

def getForks(target):
    '''
    target = repo/owner
    '''

    r = requests.get("https://api.github.com/repos/"+target+"/forks", auth=auth)

    return r.json()

def openLinks(links):
    '''
    opens the links found in tweetsWithLinks
    '''

    browserOpen = False

    for link in links:
        if browserOpen:
            webbrowser.open_new_tab(link)
        else:
            webbrowser.open_new(link)
        browserOpen = True







def dayHisto(timeList, minDate, maxDate, yLabel, labels=(), filename='gitfig.png', highlightLo=None, highlightHi=None, highlightLabel=None):
    '''
    take a list of lists 'timeList' of datetime objects, and histogram them w/ 1 bin per day
    minDate and maxDate == datetime.date objects; stack histo for each element in timeList.
    '''

    timeNum = []
    for times in timeList:
        nums = []
        for time in times:
            nums.append(dates.date2num(time))
        timeNum.append(nums)

    days = dates.DayLocator()
    fmt = dates.DateFormatter('%b-%d')
    fig = plt.figure()
    ax = fig.add_subplot(111)
    plt.xlim(minDate, maxDate)

    ax.hist(timeNum, 
        bins=range(  int(dates.date2num(minDate)), int(dates.date2num(maxDate)) +1 ), 
        align='left', 
        stacked=True,
        label = labels )

    ax.xaxis_date()
    ax.xaxis.set_major_locator(days)
    ax.xaxis.set_major_formatter(fmt)
    fig.autofmt_xdate()
    plt.ylabel(yLabel)
    if len(timeList) > 1:
        plt.legend(loc='best') 

    # shade area nicely
    if highlightHi is not None and highlightLo is not None:
        xlo = dates.datestr2num(highlightLo)
        xhi = dates.datestr2num(highlightHi)
        extra = (xhi-xlo)/2
        xlo -= extra
        xhi += extra
        ax.axvspan(xlo, xhi, color='black', alpha=0.1, hatch='.')
        shade_patch = patches.Patch(color='black', alpha=0.1, hatch='.', label=highlightLabel)
        handles, labels = ax.get_legend_handles_labels()
        handles.append(shade_patch)
        plt.legend(handles=handles, loc='best')
    
    plt.savefig(filename, bbox_inches='tight')







