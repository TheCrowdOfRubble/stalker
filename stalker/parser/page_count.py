import scrapy


def parse(response: scrapy.http.Response) -> int:
    return int(response.xpath("//div[@id='pagelist']/form/div/text()[2]").re_first(r'(?<=/).+(?=页)', 1))
