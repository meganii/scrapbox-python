'''
Scrapbox
'''

import io
import os
import json
import re
import urllib.request
from enum import Enum, auto


class ImageType(Enum):
    GYAZO = auto()
    AMAZON = auto()
    OTHER = auto()

class Scrapbox():

    domain = ''
    baseurl = ''
    image_json = {}

    def __init__(self, domain='', baseurl='', image_json_filepath=''):
        self.domain = domain
        self.baseurl = baseurl
        if not image_json_filepath == '' and os.path.exists(image_json_filepath):
            with open(image_json_filepath, 'r') as f:
                self.image_json = json.load(f)

    def indents(self, line):
        m = re.search(r'^[\t|\s]*', line)
        if m:
            return len(re.findall(r'\t|\s', m.group(0)))
        else:
            return 0

    def remove_space(self, content):
        return re.sub(r'^(\s|\t)*', '', content)

    def extract_image(self, line):
        "return taple"
        m_two_links = re.search(r'\[(.+?)\s(.+?)\]', line)
        m_one_link = re.search(r'\[(.+?)\]', line)

        if m_two_links:
            return (m_two_links.group(1), m_two_links.group(2))
        elif m_one_link:
            return (m_one_link.group(1), None)
        else:
            return ()

    def convert_list(self, line):
        '''
        Convert scrapbox list to markdown
        '''
        num_of_intends = self.indents(line)
        if not num_of_intends:
            return line
        else:
            new_line = self.remove_space(line)
            spaces = ''
            for _ in range(1, num_of_intends):
                spaces = '\t' + spaces
            return spaces + '- ' + new_line

    def insert_line_for_list(self, lines):
        new_lines = lines.copy()
        index = 0
        while index < len(new_lines):
            indents = self.indents(new_lines[index])
            if 0 < index and 0 < indents:
                prev_indents = self.indents(new_lines[index-1])
                if not prev_indents:
                    new_lines.insert(index, '')
                    index = index + 2  # Add two because insert object
                else:
                    index = index + 1
            else:
                index = index + 1
        return new_lines

    def convert_link(self, line):
        results = re.finditer(r'\[(?!\*)(.+?)\]', line)
        if not results:
            return line
        else:
            newline = line
            for result in results:
                page_title = result.group(1)
                page_url = self.to_url(page_title)
                newlink = f'[{page_title}]({self.baseurl}/{page_url})'
                newline = newline.replace(result.group(0), newlink)
            return newline

    def convert_tag(self, line):
        results = re.finditer(r'#([^\s$]*)', line)
        if not results:
            return line
        else:
            newline = line
            for result in results:
                page_title = result.group(1)
                page_url = self.to_url(page_title)
                newlink = f'[#{page_title}]({self.baseurl}/{page_url})'
                # Replace one by one because avoiding change similar word.
                newline = newline.replace(result.group(0), newlink, 1)
            return newline

    def convert_images(self, line):
        """
        lineから[IMG(src)], [IMG(src) URL]で囲われている画像データを取得し、Markdown用のタグに置き換える。
        - gyazo: 前作業でCloudinaryへアップロードしている。変換表を元に、変換後のsrcに書き換える
        - amazon: hugoのShortcodeに置き換える
        - 上記以外の画像データ: 変換表を元に、変換後のwidth, heightを計算する
        """
        images = re.finditer(r'\[(https:\/\/.+?\.(jpg|jpeg|png)|https:\/\/gyazo\.com.+?)\s*(https:\/\/.+?)?\]', line)
        newline = line
        # Convert targets
        for image in images:
            img_url = image.group(1)
            img_type = self.get_img_type(img_url)
            if img_type == ImageType.AMAZON and image.group(3):
                url = image.group(3)
                aibn = re.findall(r'https:\/\/www\.amazon\.co\.jp\/dp\/(([A-Z]|[0-9]){10})', url)
                newimg = '{{% amazon ' + aibn[0][0] + ' %}}'
                newline = newline.replace(image.group(0), newimg, 1)
                continue

            # below gyazo or other image file
            if img_type == ImageType.GYAZO:
                img_url = img_url + '/raw'
            img = self.image_json[img_url]
            newimg = '{{% img src=\"' + img_url + '\" h=\"' + \
                str(img['height']) + '\" w=\"' + str(img['width']) + '\" %}}'
            newline = newline.replace(image.group(0), newimg, 1)
        return newline

    def get_img_type(self, url):
        if re.match(r'^https:\/\/gyazo\.com', url):
            return ImageType.GYAZO
        elif re.match(r'^https:\/\/images-.+?\.ssl-images-amazon\.com\/images/.+?', url):
            return ImageType.AMAZON
        else:
            return ImageType.OTHER

    def convert_htag(self, line):
        newline = line
        tags = re.finditer(r'\[(\*+)\s(.+?)\]', newline)
        for tag in tags:
            m = re.findall(r'\*', tag.group(1))
            if m:
                stars = len(m)
                if stars > 2:
                    newtag = '# ' + tag.group(2)
                elif stars > 1:
                    newtag = '## ' + tag.group(2)
                else:
                    newtag = '### ' + tag.group(2)
                newline = newline.replace(tag.group(0), newtag, 1)
        return newline

    def extract_images(self, lines):
        results = []
        for line in lines:
            gyazo_images = re.finditer(
                r'\[(https:\/\/gyazo\.com\/.+?)\s*(https:\/\/.+?)?\]', line)
            for img in gyazo_images:
                results.append(img.group(1) + '/raw')

            images = re.finditer(
                r'\[(https:\/\/.+?\.jpg|jpeg|png)\s*(https:\/\/.+?)?\]', line)
            for img in images:
                results.append(img.group(1))
        return results

    def extract_links(self, lines):
        links = []
        for line in lines:
            results = re.finditer(r'\[(?!https?:\/\/|\*.+?)(.+?)\]', line)
            for result in results:
                links.append(result.group(1))
        return links

    def extract_tags(self, lines):
        tags = []
        for line in lines:
            results = re.finditer(r'#(.+?)(\s|$)', line)
            for result in results:
                tags.append(result.group(1))
        return tags

    def to_url(self, urlstring):
        urlstring = re.sub(r'・|!|？|&', '', urlstring)
        return re.sub(r'\(|\)|"', '-', urlstring) + '/'
        

    def to_md(self, line):
        newline = self.convert_images(line)
        newline = self.convert_list(newline)
        newline = self.convert_link(newline)
        newline = self.convert_tag(newline)
        newline = self.convert_htag(newline)  # tag
        return newline
