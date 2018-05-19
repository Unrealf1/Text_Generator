import requests
from bs4 import BeautifulSoup
import re
import peewee
import dateparser


db = peewee.SqliteDatabase('news.db')


# This is class/table of topics in db
class Themes(peewee.Model):
    name = peewee.CharField(null=False)
    description = peewee.CharField(null=False, default="No description")
    link_rbc = peewee.CharField(null=False, primary_key=True)
    last_update = peewee.DateTimeField(null=True,
                                       default=dateparser.parse('1488'))

    class Meta:
        database = db


# This is class/table of news in db
class Docs(peewee.Model):
    name = peewee.CharField(null=False)
    theme = peewee.CharField(null=False)
    description = peewee.CharField(null=True)
    link = peewee.CharField(null=False)
    last_update = peewee.DateTimeField(null=False,
                                       default=dateparser.parse('Today'))
    text = peewee.TextField(null=False)

    class Meta:
        database = db
        db_table = 'Docs'


# This is class/table which links docs with topics in db
class Tags(peewee.Model):
    teg = peewee.CharField(null=False)
    link = peewee.CharField(null=False)

    class Meta:
        database = db
        db_table = 'Tags'


# This function returns all enters of given class in the given page
def get_class_from_page(url, class_name):
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    return soup.find_all(class_=class_name)


# this function cleans text from html things
def clean_text(text):
    while re.search(r'<.*>', text, re.DOTALL) is not None:
        text = re.sub(r'<.*>', '', text, re.DOTALL)
    while re.search(r'  +', text) is not None:
        text = re.sub(r'  +', ' ', text)
    while re.search(r'\n\n+', text) is not None:
        text = re.sub(r'\n\n+', ' ', text)
    return text


def pars_main():
    print("creating database...")

    Themes.create_table()
    Docs.create_table()
    Tags.create_table()

    themes = get_class_from_page('https://www.rbc.ru/story/', 'item_story')

    for theme in themes:
        theme_name = theme.contents[1].contents[1].contents[0]
        print("name: " + theme_name)
        theme_description = str(
            theme.contents[1].contents[3].contents[0]).strip()
        print("description: ", theme_description)
        theme_link = re.findall(r"\"https\S*\"", str(theme))[0][1:-1]
        print("link: " + theme_link)

        old = Themes.select().where(Themes.link_rbc == theme_link)
        if len(old) == 0:
            cur_theme = Themes.create(name=theme_name,
                                      description=theme_description,
                                      link_rbc=theme_link)
        else:
            cur_theme = old[0]
        print()
        docs = get_class_from_page(theme_link, 'item_story-single')
        last_time = dateparser.parse('1488')
        for doc in docs:
            doc_time = doc.contents[3].contents[1].contents[0]
            print("  doc_time: ", doc_time)
            doc_name = doc.contents[1].contents[1].contents[0]
            print("  doc_name: " + doc_name)
            doc_description = doc.contents[1].contents[3].contents[0].strip()
            print("  doc_description: ", doc_description)
            doc_link = re.findall(r"\"https\S*\"", str(doc))[0][1:-1]
            print("  doc_link: " + doc_link)
            if dateparser.parse(doc_time) > cur_theme.last_update:
                doc_page = requests.get(doc_link)
                doc_soup = BeautifulSoup(doc_page.text, 'html.parser')
                doc_tags = doc_soup.find_all(class_='article__tags__link')
                print("  doc_tags:")
                for i in range(len(doc_tags)):
                    doc_tags[i] = str(doc_tags[i])
                    doc_tags[i] = re.search(r'>.*<',
                                            doc_tags[i]).group(0)[1:-1]
                    print("    " + doc_tags[i])
                    Tags.create(teg=doc_tags[i], link=doc_link)
                # print(doc_soup.findAll('p')[0])
                doc_text = ''
                for paragraph in doc_soup.findAll('p'):
                    doc_text += str(paragraph)[3:-4] + '\n'

                doc_text = clean_text(doc_text)
                Docs.create(name=doc_name, theme=theme_name,
                            description=doc_description, link=doc_link,
                            last_update=dateparser.parse(doc_time),
                            text=doc_text)
                if dateparser.parse(doc_time) > last_time:
                    last_time = dateparser.parse(doc_time)
                print()
        cur_theme.last_update = max(last_time, cur_theme.last_update)
        cur_theme.save()


if __name__ == "__main__":
    pars_main()
