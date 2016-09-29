# coding=utf-8

__author__ = 'dolacmeo'
__doc__ = '其他工具'


class Tools:
    @staticmethod
    def url_to_html_img(url):
        # 把链接生成html-img二维码
        import base64
        from io import BytesIO
        import qrcode
        qrc = qrcode.QRCode(version=1,
                            error_correction=qrcode.constants.ERROR_CORRECT_Q,
                            box_size=8,
                            border=4)
        qrc.add_data(url)
        qrc.make(fit=True)
        img = qrc.make_image()
        out = BytesIO()
        img.save(out, "PNG")
        imgstr = base64.b64encode(out.getvalue()).decode('ascii')
        img_tag = '<img src="data:image/png;base64,{0}">'.format(imgstr)
        return img_tag


if __name__ == '__main__':
    pass
