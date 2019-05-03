import scrapy


def get_page_amount(response: scrapy.http.Response) -> int:
    return int(response.xpath("//div[@id='pagelist']/form/div/text()[2]").re_first(r'(?<=/).+(?=页)', 1))
