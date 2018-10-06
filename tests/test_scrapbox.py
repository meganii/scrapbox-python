from scrapbox import Scrapbox
import unittest

class TestScrapbox(unittest.TestCase):
    '''
    test case
    '''

    def test_initialize(self):
        '''
        コンストラクタに渡した引数が設定されているか
        '''
        sb = Scrapbox()
        sb.domain = 'https://www.meganii.com'
        self.assertEqual('https://www.meganii.com', sb.domain)
        sb = Scrapbox(domain='domain', baseurl='baseurl', image_json_filepath='filepath')
        self.assertEqual('domain', sb.domain)
        self.assertEqual('baseurl', sb.baseurl)

    def test_space_1(self):
        '''
        lineの中に含まれるタブとスペースの数を返す
        '''
        sb = Scrapbox()
        line = " 1"
        self.assertEqual(1, sb.indents(line))

    def test_space_2(self):
        '''
        lineの中に含まれるタブとスペースの数を返す
        '''
        sb = Scrapbox()
        line = "  2"
        self.assertEqual(2, sb.indents(line))

    def test_tab_1(self):
        '''
        lineの中に含まれるタブとスペースの数を返す
        '''
        sb = Scrapbox()
        line = "\t1"
        self.assertEqual(1, sb.indents(line))

    def test_tab_2(self):
        '''
        lineの中に含まれるタブとスペースの数を返す
        '''
        sb = Scrapbox()
        line = "\t\t2"
        self.assertEqual(2, sb.indents(line))

    def test_tab_space(self):
        '''
        lineの中に含まれるタブとスペースの数を返す
        '''
        sb = Scrapbox()
        line = "\t 2"
        self.assertEqual(2, sb.indents(line))

    def test_remove_space(self):
        sb = Scrapbox()
        actual = sb.remove_space(' space1')
        self.assertEqual('space1', actual)

        actual = sb.remove_space('  space2')
        self.assertEqual('space2', actual)

        actual = sb.remove_space('\t \tspace3')
        self.assertEqual('space3', actual)

    def test_extract_image(self):
        line = '[https://images-fe.ssl-images-amazon.com/images/I/617BnEUVtBL.jpg]'
        sb = Scrapbox()
        actual = sb.extract_image(line)
        self.assertEqual('https://images-fe.ssl-images-amazon.com/images/I/617BnEUVtBL.jpg', actual[0])
        self.assertEqual(None, actual[1])

    def test_extract_image_has_url(self):
        line = '[https://images-fe.ssl-images-amazon.com/images/I/617BnEUVtBL.jpg https://www.amazon.co.jp/dp/B009KWTIFM]'
        sb = Scrapbox()
        actual = sb.extract_image(line)
        self.assertEqual('https://images-fe.ssl-images-amazon.com/images/I/617BnEUVtBL.jpg', actual[0])
        self.assertEqual('https://www.amazon.co.jp/dp/B009KWTIFM', actual[1])

    def test_list_markdown(self):
        line = ' test1'
        expected = '- test1'
        sb = Scrapbox()
        actual = sb.convert_list(line)
        self.assertEqual(expected, actual)

        line = '  test2'
        expected = '\t- test2'
        sb = Scrapbox()
        actual = sb.convert_list(line)
        self.assertEqual(expected, actual)

        line = '\t\t test3'
        expected = '\t\t- test3'
        sb = Scrapbox()
        actual = sb.convert_list(line)
        self.assertEqual(expected, actual)

    def test_convert_link(self):
        baseurl = 'https://mediajournal.meganii.com'
        line = '[link]'
        expected = f'[link]({baseurl}/link/)'
        sb = Scrapbox()
        sb.baseurl = baseurl
        actual = sb.convert_link(line)
        self.assertEqual(expected, actual)

    def test_convert_links(self):
        baseurl = 'https://mediajournal.meganii.com'
        line = '[link] [link2]'
        expected = f'[link]({baseurl}/link/) [link2]({baseurl}/link2/)'
        sb = Scrapbox()
        sb.baseurl = baseurl
        actual = sb.convert_link(line)
        self.assertEqual(expected, actual)


    def test_convert_tag(self):
        baseurl = 'https://mediajournal.meganii.com'
        line = '#tag'
        expected = f'[#tag]({baseurl}/tag/)'
        sb = Scrapbox()
        sb.baseurl = baseurl
        actual = sb.convert_tag(line)
        self.assertEqual(expected, actual)


    def test_convert_tags(self):
        baseurl = 'https://mediajournal.meganii.com'
        line = '#tag #tag2'
        expected = f'[#tag]({baseurl}/tag/) [#tag2]({baseurl}/tag2/)'
        sb = Scrapbox()
        sb.baseurl = baseurl
        actual = sb.convert_tag(line)
        self.assertEqual(expected, actual)


    def test_convert_actual_data(self):
        line = '\t表面利回り = (満室時の年間家賃収入 / 物件の購入価格) * 100'
        sb = Scrapbox()
        expected = 1
        actual = sb.indents(line)
        self.assertEqual(expected, actual)

    def test_insrt_line_for_list(self):
        lines = ['Title', ' list1', ' list2', '  list 1.1']
        expected = ['Title', '', ' list1', ' list2', '  list 1.1']
        sb = Scrapbox()
        actual = sb.insert_line_for_list(lines)
        self.assertEqual(expected, actual)

    def test_extract_images(self):
        '''
        Target
         - http://gyazo.com
         - http?://.+?\.(png|img)
        '''
        lines = ['[https://gyazo.com/5f93e65a3b979ae5333aca4f32600611]']
        expected = 'https://gyazo.com/5f93e65a3b979ae5333aca4f32600611/raw'
        sb = Scrapbox()
        actual = sb.extract_images(lines)
        self.assertEqual(expected, actual[0])

    def test_convert_images(self):
        line = '[https://images-na.ssl-images-amazon.com/images/I/51aMASBzCCL._SX350_BO1,204,203,200_.jpg https://www.amazon.co.jp/dp/4592145119]'
        sb = Scrapbox()
        expected = '{{% amazon 4592145119 %}}'
        actual = sb.convert_images(line)
        self.assertEqual(expected, actual)

    def test_convert_gyazo_image(self):        
        line = '[https://gyazo.com/c3a68ab8928396608ef24349051c9d71]'
        sb = Scrapbox(image_json_filepath='./tests/images.json')
        expected = '{{% img src="https://gyazo.com/c3a68ab8928396608ef24349051c9d71/raw" h="212" w="379" %}}'
        actual = sb.convert_images(line)
        self.assertEqual(expected, actual)

    def test_extract_link(self):
        lines = [
            '[Test]Link',
        ]
        sb = Scrapbox()
        expected = ['Test']
        actual = sb.extract_links(lines)
        self.assertEqual(expected, actual)

    def test_extract_tag(self):
        lines = [
            '#Tags1 #Tags2',
        ]
        sb = Scrapbox()
        expected = ['Tags1', 'Tags2']
        actual = sb.extract_tags(lines)
        self.assertEqual(expected, actual)
    
    def test_convert_to_htag(self):
        line = '[* Test]'
        sb = Scrapbox()
        expected = '### Test'
        actual = sb.convert_htag(line)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
