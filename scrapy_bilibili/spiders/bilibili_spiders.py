from scrapy import Spider, Request
from scrapy_bilibili.items import BilibiliVideoListItem
from util import json2obj
import requests

# 获取tag
# https://api.bilibili.com/x/web-interface/view/detail/tag?aid=686455463&cid=789251766
# {"code":0,"message":"0","ttl":1,"data":[{"tag_id":6348,"tag_name":"水果","cover":"http://i0.hdslb.com/bfs/tag/d315c5cb31d9db127ff054f5f0b91c9cb047fc64.png","head_cover":"http://i0.hdslb.com/bfs/tag/01f09c2d8ebe8d360a9ef762ef5995f2e8b046aa.png","content":"","short_content":"","type":0,"state":0,"ctime":1436866637,"count":{"view":0,"use":159510,"atten":21491},"is_atten":0,"likes":0,"hates":0,"attribute":0,"liked":0,"hated":0,"extra_attr":0,"music_id":"","tag_type":"new_channel","is_activity":false,"color":"#FB7199","alpha":60,"is_season":false,"subscribed_count":21491,"archive_count":"12.2万","featured_count":1285,"jump_url":""},{"tag_id":20215,"tag_name":"美食","cover":"http://i0.hdslb.com/bfs/tag/398c37294bcf254d6465faa49eee981854150925.png","head_cover":"http://i0.hdslb.com/bfs/tag/6b939a192022a44297798574ea629c6d2915048e.png","content":"好饿好饿好饿，我真的好饿~","short_content":"一到夜里，美食圈露出了…… ","type":3,"state":0,"ctime":1436866637,"count":{"view":0,"use":5053475,"atten":2037868},"is_atten":0,"likes":0,"hates":0,"attribute":0,"liked":0,"hated":0,"extra_attr":0,"music_id":"","tag_type":"new_channel","is_activity":false,"color":"#B07542","alpha":60,"is_season":false,"subscribed_count":2037868,"archive_count":"944.9万","featured_count":46269,"jump_url":""},{"tag_id":5417,"tag_name":"科普","cover":"http://i0.hdslb.com/bfs/tag/71902f861384bf7b9feccf2e53511a2470335886.png","head_cover":"http://i0.hdslb.com/bfs/tag/108b76557e39013310f0de189feccf14b8a6927b.png","content":"为何？如何？因何?我们总想去了解自己未知的事物。","short_content":"世上总有你好奇的事儿","type":3,"state":0,"ctime":1436866637,"count":{"view":0,"use":1864299,"atten":1730685},"is_atten":0,"likes":0,"hates":0,"attribute":0,"liked":0,"hated":0,"extra_attr":0,"music_id":"","tag_type":"new_channel","is_activity":false,"color":"#394858","alpha":60,"is_season":false,"subscribed_count":1730685,"archive_count":"1467.9万","featured_count":37428,"jump_url":""},{"tag_id":138489,"tag_name":"健康养生","cover":"","head_cover":"","content":"","short_content":"","type":0,"state":0,"ctime":1436866637,"count":{"view":0,"use":24018,"atten":288},"is_atten":0,"likes":0,"hates":0,"attribute":0,"liked":0,"hated":0,"extra_attr":0,"music_id":"","tag_type":"old_channel","is_activity":false,"color":"","alpha":0,"is_season":false,"subscribed_count":288,"archive_count":"-","featured_count":0,"jump_url":""},{"tag_id":2503953,"tag_name":"Vlog","cover":"","head_cover":"","content":"","short_content":"","type":0,"state":0,"ctime":1471257832,"count":{"view":0,"use":478095,"atten":3239},"is_atten":0,"likes":0,"hates":0,"attribute":0,"liked":0,"hated":0,"extra_attr":0,"music_id":"","tag_type":"old_channel","is_activity":false,"color":"","alpha":0,"is_season":false,"subscribed_count":3239,"archive_count":"-","featured_count":0,"jump_url":""},{"tag_id":3374483,"tag_name":"桑葚","cover":"","head_cover":"","content":"","short_content":"","type":0,"state":0,"ctime":1491431507,"count":{"view":0,"use":1676,"atten":16},"is_atten":0,"likes":0,"hates":0,"attribute":0,"liked":0,"hated":0,"extra_attr":0,"music_id":"","tag_type":"old_channel","is_activity":false,"color":"","alpha":0,"is_season":false,"subscribed_count":16,"archive_count":"-","featured_count":0,"jump_url":""}]}

# 获取video list不带tag需要根据上边再获取
# https://api.bilibili.com/x/web-interface/newlist?rid=201&type=0&ps=30&pn=1
# "page":{"count":2425217,"num":1,"size":30}

# 获取最近一段时间的video list带有tag
# https://s.search.bilibili.com/cate/search?main_ver=v3&search_type=video&view_type=hot_rank&copy_right=-1&new_web_tag=1&order=click&cate_id=201&page=1&pagesize=50&time_from=20221006&time_to=20221113
# "numPages": 5294,"numResults": 264681,"crr_query": "","pagesize": 50,"suggest_keyword": "","egg_info": null,"cache": 0,"exp_bits": 1,"exp_str": "","seid": "13218235806365448668","msg": "success","egg_hit": 0,"page": 1

# 5581

class BilibiliSpider(Spider):
    # Spider名字
    name = 'BilibiliSpider'

    # 视频列表链接模版 （三个参数）
    url_fmt = r'https://api.bilibili.com/x/web-interface/newlist?rid={rid}&type=0&ps={ps}&pn={pn}'

    def __init__(self, *args, rid: int=201, ps: int=50, **kwargs):
        """ 
            rid: 区ID 默认201 表示知识区
            ps: 视频列表每页视频数量
        """
        super().__init__(*args, **kwargs)
        self.rid = rid
        self.ps = ps
        # 视频列表链接模版 （一个参数）
        self.url = self.url_fmt.format(rid=rid, ps=ps, pn='{}')
        # 初始链接
        self.start_urls = [self.url.format(1909)]

    def parse(self, response):
        """页面解析"""
        def get_tags(aid, cid):
            url = f"https://api.bilibili.com/x/web-interface/view/detail/tag?aid={aid}&cid={cid}"
            res = requests.get(url).json()['data']
            tag = ','.join([t['tag_name'] for t in res])
            return tag

        url = response.url
        pn = int(url.rsplit('=', 1)[-1])  # 视频列表页码
        page = response.body.decode('UTF-8')  # 响应对象中的json文件
        obj = json2obj(page)  # 转成Python对象
        data = obj['data']
        count = data['page']['count']  # 该区当前视频总数
        archives = data['archives']
        for i in archives:
            aid = i['aid']
            bvid = i['bvid'].strip()
            cid = i['cid']

            # tid = i['tid']
            # pic = i['pic'].strip()
            title = i['title'].strip()
            desc = i['desc'].strip()
            tag = get_tags(aid, cid)
            # duration = i['duration']
            # videos = i['videos']
            # pubdate = i['pubdate']

            stat = i['stat']
            view = stat['view']
            danmaku = stat['danmaku']
            reply = stat['reply']
            like = stat['like']
            dislike = stat['dislike']
            coin = stat['coin']
            favorite = stat['favorite']
            share = stat['share']

            # owner = i['owner']
            # mid = owner['mid']
            # name = owner['name'].strip()
            # face = owner['face'].strip()

            # 封装成Item对象
            item = BilibiliVideoListItem(
                aid=aid,
                bvid=bvid,
                cid=cid,

                # tid=tid,
                # pic=pic,
                title=title,
                desc=desc,
                tag=tag,
                # duration=duration,
                # videos=videos,
                # pubdate=pubdate,

                view=view,
                danmaku=danmaku,
                reply=reply,
                like=like,
                dislike=dislike,
                coin=coin,
                favorite=favorite,
                share=share,

                # mid=mid,
                # name=name,
                # face=face,
            )
            yield item

        if pn * self.ps < count:  # 如果当前爬取的视频数量少于视频总数
            url = self.url.format(pn+1)  # 下一页的页码
            req = Request(url, callback=self.parse)  # 下一页的请求对象
            yield req


if __name__=='__main__':
    s = '''{"code":0,"message":"0","ttl":1,"data":{"archives":[{"aid":243910595,"videos":1,"tid":76,"tname":"美食圈","copyright":1,"pic":"http://i0.hdslb.com/bfs/archive/0e13801f9670e8dda8cce15f8090dfacf78f0bea.png","title":"最简单的肉末酱茄子做法！不油不腻，老下饭了！","pubdate":1595396780,"ctime":1595396780,"desc":"肉末酱茄子不油不腻老下饭了","state":0,"attribute":16384,"duration":83,"rights":{"bp":0,"elec":0,"download":0,"movie":0,"pay":0,"hd5":0,"no_reprint":0,"autoplay":1,"ugc_pay":0,"is_cooperation":0,"ugc_pay_preview":0,"no_background":0},"owner":{"mid":638628553,"name":"user_76365067632","face":"http://i0.hdslb.com/bfs/face/1e3e260ad5a14d0dafdd0e1a84eb213ddb7bac95.jpg"},"stat":{"aid":243910595,"view":0,"danmaku":0,"reply":0,"favorite":0,"coin":0,"share":0,"now_rank":0,"his_rank":0,"like":0,"dislike":0},"dynamic":"","cid":215272733,"dimension":{"width":720,"height":1280,"rotate":0},"bvid":"BV1Nv411q78E"}],"page":{"count":1821990,"num":1,"size":1}}}'''
    obj = json2obj(s)

    def get_tags(aid, cid):
        url = f"https://api.bilibili.com/x/web-interface/view/detail/tag?aid={aid}&cid={cid}"
        res = requests.get(url).json()['data']
        tag = ','.join([t['tag_name'] for t in res])
        return tag

    data = obj['data']
    count = data['page']['count']
    archives = data['archives']
    for i in archives:
        aid = i['aid']
        bvid = i['bvid'].strip()
        cid = i['cid']

        # tid = i['tid']
        # pic = i['pic'].strip()
        title = i['title'].strip()
        desc = i['desc'].strip()
        tag = get_tags()
        # duration = i['duration']
        # videos = i['videos']
        # pubdate = i['pubdate']

        stat = i['stat']
        view = stat['view']
        danmaku = stat['danmaku']
        reply = stat['reply']
        like = stat['like']
        dislike = stat['dislike']
        coin = stat['coin']
        favorite = stat['favorite']
        share = stat['share']

        # owner = i['owner']
        # mid = owner['mid']
        # name = owner['name'].strip()
        # face = owner['face'].strip()

        item = BilibiliVideoListItem(
            aid=aid,
            bvid=bvid,
            cid=cid,

            # tid=tid,
            # pic=pic,
            title=title,
            desc=desc,
            # duration=duration,
            # videos=videos,
            # pubdate=pubdate,

            view=view,
            danmaku=danmaku,
            reply=reply,
            like=like,
            dislike=dislike,
            coin=coin,
            favorite=favorite,
            share=share,

            # mid=mid,
            # name=name,
            # face=face,
        )
        print(item)
