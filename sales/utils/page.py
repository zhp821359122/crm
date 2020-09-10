from django.utils.safestring import mark_safe


class MyPagination(object):
    """
     page_num：当前请求的分页数
     total_page：总页码
     page_range_count：分页组件中加载的页码数量 7
     base_url: 组件中a标签的根地址 /customer/ 可以request.path取出来

     get_html返回安全的可以直接在页面中渲染的分页组件
    """
    def __init__(self, page_num, total_page, page_range_count, base_url):
        if page_num <= int(page_range_count / 2):
            page_range = range(1, page_range_count + 1)  # page_range 循环生成分页组件a标签时用到的每一页的页码
        elif page_num >= (total_page - int(page_range_count / 2)):
            page_range = range(total_page - page_range_count, total_page + 1)
        else:
            page_range = range(page_num - 3, page_num + 4)
        self.page_num = page_num
        self.page_range = page_range
        self.total_page = total_page
        self.base_url = base_url

    def get_html(self):
        html = ''
        # class ="text-center" 让分页组件居中
        html += '<nav aria-label="Page navigation" class="text-center"><ul class="pagination">'
        html += '<li><a href="{}?page=1" aria-label="First">'.format(self.base_url)
        html += '<span aria-hidden="true">&laquo;</span></a></li>'
        for page in self.page_range:  # 由于数字不能在模板中for循环 所以得先弄个可迭代对象出来 用range左闭右开
            if page == self.page_num:
                html += '<li class="active"><a href="{1}?page={0}">{0}</a></li>'.format(page, self.base_url)
            else:
                html += f'<li><a href="{self.base_url}?page={page}">{page}</a></li>'
        html += f' <li><a href="{self.base_url}?page={self.total_page}" aria-label="Last">'
        html += '<span aria-hidden="true">&raquo;</span></a></li></ul></nav>'
        return mark_safe(html)
