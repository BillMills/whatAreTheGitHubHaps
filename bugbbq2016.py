import whatAreTheGitHubHaps as ghh
import pprint
import datetime, pytz

pp = pprint.PrettyPrinter(indent=4)
repos = [
'swcarpentry/shell-novice',
'swcarpentry/git-novice',
'swcarpentry/hg-novice',
'swcarpentry/sql-novice-survey',
'swcarpentry/python-novice-inflammation',
'swcarpentry/r-novice-inflammation',
'swcarpentry/r-novice-gapminder',
'swcarpentry/matlab-novice-inflammation',
'swcarpentry/make-novice',
'swcarpentry/instructor-training',
'alex-konovalov/gap-lesson',
'ropenscilabs/r-docker-tutorial'
]

minDate = datetime.date.fromordinal(736114) #May 31, 2016
maxDate = datetime.date.fromordinal(736129) #June 14, 2015

#############
# Pull Requests
#############

pulls = [] 
for repo in repos:
    pulls += ghh.fetchPulls(repo, datetime.datetime(2016, 5, 31, 0, 0, 0, 0, pytz.UTC))

# generate stacked plot of each type of PR: open, merged & rejected
submittedPulls = ghh.submittedPulls(pulls)
mergedPulls = ghh.mergedPulls(pulls)
rejectedPulls = ghh.rejectedPulls(pulls)

submittedTimes = ghh.tidyTime(submittedPulls, minDate, maxDate)
rejectedTimes = ghh.tidyTime(rejectedPulls, minDate, maxDate)
mergedTimes = ghh.tidyTime(mergedPulls, minDate, maxDate)

plot = ghh.dayHisto([submittedTimes, mergedTimes, rejectedTimes], minDate, maxDate, 
    'PRs/day', ('Submitted', 'Merged', 'Rejected'), 'bbqPulls.png')

