import re
from django.utils.safestring import mark_safe


class MyPagination(object):
    """
     page_num：当前请求的分页数
     total_page：总页码
     page_range_count：分页组件中加载的页码数量 7
     request: 当前url的request对象 用来提取GET请求后面携带的除了page以外的其他参数  格式为&search_field=qq&kw=111或者为空 提取逻辑直接封装到分页组件中来

     get_html返回安全的可以直接在页面中渲染的分页组件
    """
    def __init__(self, request, page_num, total_page, page_range_count):
        if page_num <= int(page_range_count / 2):
            page_range = range(1, page_range_count + 1)  # page_range 循环生成分页组件a标签时用到的每一页的页码
        elif page_num >= (total_page - int(page_range_count / 2)):
            page_range = range(total_page - page_range_count, total_page + 1)
        else:
            page_range = range(page_num - 3, page_num + 4)
        #  如果总的页码数小于分页组件中默认加载的页码数量 7
        if total_page < page_range_count:
            page_range = range(1, total_page+1)
        # 使用正则替代 完美提取GET请求中除了page以外的其他参数 &search_field=qq&kw=111
        if request.GET.get('page'):
            param = re.sub('page=\d+', '', request.GET.urlencode())
        elif not request.GET.urlencode():
            param = request.GET.urlencode()
        else:
            param = '&' + request.GET.urlencode()
        self.page_num = page_num
        self.page_range = page_range
        self.total_page = total_page
        self.base_url = request.path  # base_url: 组件中a标签的根地址 /customer/ 可以request.path取出来
        self.param = param

    def get_html(self):
        html = ''
        # class ="text-center" 让分页组件居中
        html += '<nav aria-label="Page navigation" class="text-center"><ul class="pagination">'
        html += '<li><a href="{}?page=1{}" aria-label="First">'.format(self.base_url, self.param)
        html += '<span aria-hidden="true">&laquo;</span></a></li>'
        for page in self.page_range:  # 由于数字不能在模板中for循环 所以得先弄个可迭代对象出来 用range左闭右开
            if page == self.page_num:
                html += '<li class="active"><a href="{1}?page={0}{2}">{0}</a></li>'.format(page, self.base_url, self.param)
            else:
                html += f'<li><a href="{self.base_url}?page={page}{self.param}">{page}</a></li>'
        html += f' <li><a href="{self.base_url}?page={self.total_page}{self.param}" aria-label="Last">'
        html += '<span aria-hidden="true">&raquo;</span></a></li></ul></nav>'
        return mark_safe(html)
