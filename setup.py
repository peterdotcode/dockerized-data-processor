import datetime
import re
from bs4 import BeautifulSoup
import requests
import sys
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, DateTime, create_engine, select
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d,%H:%M:%S',filename='setup.log',level=logging.INFO)

r  = requests.get(r"http://export.arxiv.org/rss/cs")
data = r.text
soup = BeautifulSoup(data,"xml")

engine = create_engine('sqlite:///test.db')
metadata = MetaData()

arxiv_cs_publications = Table('arxiv_cs_publications', metadata,
    Column('publication_id', Integer, primary_key=True),
    Column('title', String),
    Column('description', String),
    Column('subject', String),
    Column('version', String),
    Column("created_date",DateTime, default=datetime.datetime.utcnow)
    ,)

metadata.create_all(engine)
ins_publication = arxiv_cs_publications.insert()
conn = engine.connect()

#Loop through each item in the RSS feed
for i in soup.find_all('item'):
    #get the title text
    RawTitleText = i.title.get_text()

    #Caputure end of title string eg. "(arXiv:1810.08276v3 [cs.DS] UPDATED)"
    TitleMetaRegex = re.compile(r'(\(arXiv:*.*\))')
    TitleMeta  = TitleMetaRegex.search(RawTitleText).group()

    #Get the ID like "1810.08276v3"
    TitleMetaRegex_version = re.compile(r'(\d.\d*.\d.\d*\D\d.)')
    VersionID =  TitleMetaRegex_version.search(TitleMeta).group()

    #Check if the ID exits in the database
    s = select([arxiv_cs_publications.c.publication_id]).where(arxiv_cs_publications.c.version == VersionID)
    results = conn.execute(s)
    sqlReturn = results.fetchall()

    #If the ID does not exists in the database
    if not sqlReturn:
        #capture subject from the title eg:  [cs.DS]
        TitleText= re.sub(TitleMetaRegex,'', RawTitleText)
        TitleMetaRegex_subject = re.compile(r'\[(.*?)\]')
        TitleSubject = TitleMetaRegex_subject.search(TitleMeta).group()
        #remove leading '[' and trailing ']'
        TitleSubject = TitleSubject[1:-1]

        #Get the description
        Description = i.description.get_text()
        #Remove the leading and trailing <p>
        Description = Description.replace("<p>", "").replace("</p>", "")

        ins = ins_publication.values(title=TitleText,description=Description,subject=TitleSubject,version=VersionID)
        logging.info('inseting record for %s', VersionID)

        result = conn.execute(ins)
    else:
        logging.info('record for %s exists in the database, nothing to add',VersionID)
