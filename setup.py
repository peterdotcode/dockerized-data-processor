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
    Column('entry_id', Integer, primary_key=True),
    Column('title', String),
    Column('description', String),
    Column('subject', String),
    Column('publication_id', String),
    Column('publication_version', String),
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

    #split version id string into publication_id and publication_version
    SplitID = re.split('[v]',VersionID)
    ID = SplitID[0]
    Version = SplitID[1]

    #Check if the ID exits in the database
    s = select([arxiv_cs_publications.c.publication_id]).where(arxiv_cs_publications.c.publication_id == ID).where(arxiv_cs_publications.c.publication_version==Version)
    results = conn.execute(s)
    sqlReturn = results.fetchall()

    #If the ID does not exists in the database
    if not sqlReturn:

        #Title less the meta data
        TitleText= re.sub(TitleMetaRegex,'', RawTitleText)

        #capture subject from the title eg:  [cs.DS]
        TitleSubject = re.findall(r'\[(.*?)\]',RawTitleText)
        TitleSubject = TitleSubject[0]

        #Get the description
        Description = i.description.get_text()
        #Remove the leading and trailing <p>
        Description = Description.replace("<p>", "").replace("</p>", "")

        insert = ins_publication.values(title=TitleText,description=Description,subject=TitleSubject,publication_id=ID, publication_version=Version)
        logging.info('inseting record for %s version %s', ID, Version)

        conn.execute(insert)
    else:
        logging.info('record for %s exists in the database, nothing to add',VersionID)
