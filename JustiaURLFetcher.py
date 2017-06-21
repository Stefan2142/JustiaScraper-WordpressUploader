from lxml import html
from lxml import etree
import lxml.html
from bs4 import BeautifulSoup
import urllib2, time

base_url='http://law.justia.com'
# List with excluded url 
excluded_l=['front-matter', 'front']

# Simple helper function to connect to a parser URL
# and return BeautifulSoup object back to main program.
def connect(url):
    site = url
    hdr = {'User-Agent': 'Mozilla/5.0'}
    ans=False
    while ans == False:
	    try:
	        req = urllib2.Request(site,headers=hdr)
	        page = urllib2.urlopen(req)
	        soup = BeautifulSoup(page,'html.parser')
	        ans = True
	    except Exception as e:
	    	print e
	        continue
    return soup

def getURLs(year):
    links=[]
    soup = connect('http://law.justia.com/codes/us')
    url_list=[]
    result = soup.find('div',{'class':'wrapper jcard has-padding-30 blocks'})
    c1=result.find('ul')
    counter=0
    root=etree.Element('root')
    root_l=list()
    # Pretty much all errors are dealt within connect() function or 
    # in if statements below in code.
    # So if anything else comes up, abort
    try:
	    for a1 in c1.findAll('a'):
	        counter+=1
	        print a1['href']
	        if year in a1['href']:
		        child1=etree.Element('level1')
		        child1.text=a1['href']
		        root.append(child1)
		        root_l.append(a1['href'])
		        soup=connect(base_url+a1['href'])
		        result = soup.find('div',{'class':'wrapper jcard has-padding-30 blocks'})
		        c2=result.find('ul') # All results are stored in unordered list
		        for a2 in c2.findAll('a'): # Look for all anchor links in <ul>
		            counter+=1
		            # Determine the level of 'deepnes', how far deep are we in the website structure
		            # It's based on number of occurances of '/' in the url
		            if (base_url+a2['href']).count('/') <8: 
		                print'    ', base_url+a2['href']
		                child2=etree.Element('level1')
		                child2.text=a2['href']
		                child1.append(child2)
		                root_l.append(a2['href'])
		                soup=connect(base_url+a2['href'])
		                result = soup.find('div',{'class':'wrapper jcard has-padding-30 blocks'})
		                c3=result.find('ul')
		                for a3 in c3.findAll('a'): # Iterate through all anchor links found in previous for loop
		                    counter+=1
		                    if (base_url+a3['href']).count('/')<9 and not any(x in a3['href'] for x in excluded_l):
		                        print '        ',base_url+a3['href']
		                        child3=etree.Element('level1')
		                        child3.text=a3['href']
		                        child2.append(child3)
		                        root_l.append(a3['href'])
		                        soup=connect(base_url+a3['href'])
		                        result = soup.find('div',{'class':'wrapper jcard has-padding-30 blocks'})
		                        c4=result.find('ul')
		                        if c4 is not None:
		                            for a4 in c4.findAll('a'):
		                                counter+=1
		                                if (base_url+a4['href']).count('/') < 10 and not any(x in a4['href'] for x in excluded_l):
		                                    print '            ', base_url+a4['href']
		                                    child4=etree.Element('level1')
		                                    child4.text=a4['href']
		                                    child3.append(child4)
		                                    root_l.append(a4['href'])
		                                    soup=connect(base_url+a4['href'])
		                                    result = soup.find('div',{'class':'wrapper jcard has-padding-30 blocks'})
		                                    c5=result.find('ul')
		                                    if c5 is not None:
		                                        for a5 in c5.findAll('a'):
		                                            counter+=1
		                                            if (base_url+a5['href']).count('/') < 11 and not any(x in a5['href'] for x in excluded_l):
		                                                child5=etree.Element('level1')
		                                                child5.text=a5['href']
		                                                child4.append(child5)
		                                                root_l.append(a5['href'])
		                                                print '                ', base_url+a5['href']
		                                                soup = connect(base_url+a5['href'])
		                                                result = soup.find('div',{'class':'wrapper jcard has-padding-30 blocks'})
		                                                c6 = result.find('ul')
		                                                if c6 is not None:
		                                                    for a6 in c6.findAll('a'):
		                                                        counter+=1
		                                                        if (base_url+a6['href']).count('/') < 12 and not any(x in a6['href'] for x in excluded_l):
		                                                            print '                    ', base_url+a6['href']
		                                                            child6=etree.Element('level1')
		                                                            child6.text=a6['href']
		                                                            child5.append(child6)
		                                                            root_l.append(a6['href'])
		                                                            soup = connect(base_url+a6['href'])
		                                                            result = soup.find('div',{'class':'wrapper jcard has-padding-30 blocks'})
		                                                            c7 = result.find('ul')
		                                                            if c7 is not None:
		                                                                for a7 in c7.findAll('a'):
		                                                                    counter+=1
		                                                                    if (base_url+a7['href']).count('/') < 13 and not any(x in a7['href'] for x in excluded_l):
		                                                                        print '                        ', base_url+a7['href']
		                                                                        child7=etree.Element('level1')
		                                                                        child7.text=a7['href']
		                                                                        child6.append(child7)
		                                                                        root_l.append(a7['href'])
    except:
    	return root_l

    return root_l



# List of years from which to get URL
# This part is manually changed since automating it,
# would cause significant load on server.
year_list=['2008','2009','2010','2011','2012','2013','2014']
for year in year_list:
	root = getURLs(year)
	with open(str(year)+'.txt','a') as f:
		for i in root:
			f.write(i+'\r\n')
