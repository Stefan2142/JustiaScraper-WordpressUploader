from lxml import html
from lxml import etree
from lxml.html import fromstring
import xlsxwriter
import requests
import time
import lxml.html
from bs4 import BeautifulSoup
import urllib2
import re
from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc import WordPressPage
from wordpress_xmlrpc.methods import taxonomies
from wordpress_xmlrpc.methods import posts
from socket import error as SocketError
import errno


def connect(url):
    hdr = {'User-Agent': 'Mozilla/5.0'}
    try:
        req = urllib2.Request(url,headers=hdr)
        page = urllib2.urlopen(req)
    except:
    	print 'Detected an request error, waiting five seconds.'
    	time.sleep(5)
        req = urllib2.Request(url, headers=hdr)
        page = urllib2.urlopen(req)


    try: # Connection reset by peer
    	soup = BeautifulSoup(page,'html.parser') 
    except SocketError:
    	print 'Detected socket error, waiting five seconds.'
    	time.sleep(5)
    	try:
    		soup = BeautifulSoup(page,'html.parser')
    	except httplib.IncompleteRead as e:
    		print 'Detected IncompleteRead error'
    		soup = BeautifulSoup(page.partial,'html.parser')
    return soup


def main():
	fileName = '2000.txt'
	base_url='https://law.justia.com'
	url_list=[]
	# Source file with links to scrape and upload
	with open(fileName,'r') as f:
		url_list=f.readlines()

	# Main loop
	for page in url_list[:]:
		full_link=base_url+page.strip()
		soup = connect(full_link)
		cat_list=[]
		
		# Navigation elements:
		nav = soup.find('nav',{'class':'breadcrumbs small-font font-helvetica'})

		print '\nStarting with url:', base_url+page.strip()

		if not nav.contents[-1].strip().encode('utf-8'):
			c=nav.prettify().split('<span class="breadcrumb-separator">')
			soup2=BeautifulSoup(''.join(c).replace("\n",'').replace('<em>',''),'html.parser')
			tmp=[]
			for i in soup2: tmp.append(i)
			tag=tmp[-1].replace('   ',' ').strip().encode('utf-8')
			print 'Tag:', tag
		else:
			tag = nav.contents[-1].strip().encode('utf-8')
			print 'Tag:', tag

		# Getting categories:
		for i in nav.findAll('a'):
			if not i.text == None and not i.text == 'Justia':
				cat_list.append(i.text)	
		print 'Category:',cat_list


		# Getting Title
		title = soup.find('h1').get_text(' ')
		title2 = soup.find('h1').get_text('<br>')
		print 'Title:',title.encode('utf-8')

		# Getting rid of Title(h1), Metadata links, Download PDF links, Front Matter links
		[x.extract() for x in soup.findAll('h1')]
		try:
			[x.extract() for x in soup.find('a',{'id':'metadata-link'})]
			[x.extract() for x in soup.find('div',{'id':'metadata'})]
		except TypeError:
			'Possible type error when trying to remove "metadata" references.'

		try:
			[x.extract() for x in soup('li',text=re.compile('Front Matter'))]
		except AttributeError:
			"Probably element 'Front Matter' wasn't found"
		try:
			[x.extract() for x in soup.find('div',{'class':'downloadlink'})]
		except TypeError:
			'Possible type error when trying to remove "downloadLink"'
		[x.extract() for x in soup('a', text=re.compile('Download PDF'))]
		# Remove tags that don't contain any text
		[x.extract() for x in soup.findAll() if x.text.isspace()]



		results = soup.find('div',{'class':'wrapper jcard has-padding-30 blocks'})


		# Body of page
		body = unicode(results).replace('\\n','').replace('<br>','').replace("</br>","")

		# Dealing with internal navigation
		try:
			for a in soup.findAll('a'):
				a['href']=a['href'].replace('index.html','')
				a['href']=a['href'].replace('/','')
		except KeyError:
			print 'Some key error when dealing with internal link navigation;'


		cat_list.append(tag)
		for i in range(len(cat_list)): cat_list[i]=cat_list[i][:180]
	
		# Wordpress procedures:
		# Used for retrying if there was an error while uploading
		retries=0 
		retries_bool=False
		while retries<4:
			try:
				client = Client('https://www.statutebase.com/xmlrpc.php','<USERNAME>','<PASSWORD')
				body = unicode(results).replace('\\n','').replace('<br>','').replace("</br>","")
				post = WordPressPost()
				post.title = title2[:100]
				post.slug=page.replace('/','')
				post.post_status = 'publish'
				post.content = body

				post.terms_names = {
				        'post_tag': cat_list[2:],
				        'category': cat_list[:2],
				}

				post.id = client.call(posts.NewPost(post))
				retries=5
				retries_bool=True
				print 'Article uploaded!'
			except Exception as e:
				time.sleep(5)
				retries=retries+1
				retries_bool=False
				if '500' in e:
					print 'Error 500 detected. Skipping current article'
					retries=True
				print 'Error while trying to upload:',e
				pass
		if retries_bool==False:
			with open(fileName[:fileName.find('.txt')]+'_errors.txt','a') as f:
				f.write(page.strip()+'\n') # Write url on which error occured
		time.sleep(0.5)

if __name__ == '__main__':
	main()
