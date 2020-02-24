from collections import defaultdict

import validators
from flask import request
from flask_restplus import Api, Resource, fields
from werkzeug.utils import redirect

from app import create_app, cache, LOGGER
from commons.utils import shortname_generator, get_reserved_short_names
from config import Config
from models.url_shortner import UrlShortnerMapping
from schemas.url_shortner import url_shortner_schema_multi

main_app = create_app()
api = Api(main_app, doc='/documentation')

urlshortner_post_fields = {
    "url": fields.Url(required=True, description='url to short'),
    "short_name": fields.String(description='shortname for the url')
}

urlshortner_post = api.model('URLShortner', urlshortner_post_fields)


class ShortName():
    def get_url_shortner(self, **query):
        return UrlShortnerMapping.query.filter_by(**query).first()

    def get_random_short_name(self):
        while True:
            short_name = shortname_generator()
            if not self.get_url_shortner(short_name=short_name):
                break
        return short_name

    def check_short_name(self, short_name):
        reserved_names = get_reserved_short_names()
        check_short_name = short_name and short_name in reserved_names \
                           or short_name and self.get_url_shortner(short_name=short_name)\
                           or short_name and not validators.slug(short_name)
        return check_short_name


@api.route('/shortner')
class URLShortner(Resource, ShortName):

    @api.response(200, 'Successfully retrieves all urls')
    def get(self):
        '''List all shorterned urls'''

        res = {
            'success': True,
            'message': 'url does not exist',
            'data': url_shortner_schema_multi.dump(UrlShortnerMapping.query.all()),
        }
        return res, 200

    @api.response(200, 'Successfully shortened the url')
    @api.expect(urlshortner_post, validate=True)
    def post(self):
        data = request.json

        url = data.get('url')

        if not validators.url(url):
            res = {
                'success': False,
                'message': 'Please enter a valid url with protocol (http, https)',
                'data': {},
            }
            return res, 400

        url_shortner = self.get_url_shortner(url=url)

        if url_shortner:
            res = {
                'success': False,
                'message': 'Shortned url already exists for the url',
                'data': url_shortner.url,
            }
            return res, 200

        short_name = data.get('short_name')

        check_short_name = self.check_short_name(short_name)
        if check_short_name:
            res = {
                'success': False,
                'message': 'Shortname already exists choose a different name',
                'data': {},
            }
            return res, 400

        if not short_name:
            short_name = self.get_random_short_name()
            data['short_name'] = short_name

        url_shortner_mapping = UrlShortnerMapping(**data)
        url_shortner_mapping.save()

        res = {
            'success': True,
            'message': 'URL shortner successfully created',
            'data': {'shortned_url': f'{Config.DOMAIN_URL}/{short_name}'},
        }
        return res, 200


@api.route('/time_series_plot')
class TimeSeriesPlot(Resource):

    @api.response(200, 'Successfully retrieves all urls')
    def get(self):
        time_series_dict = defaultdict(int)
        for url_shortner in UrlShortnerMapping.query.all():
            dt = url_shortner.created_at.strftime("%Y-%m-%d")
            time_series_dict[dt] += 1
        time_series_data = []
        for date, count in time_series_dict.items():
            time_series_data.append({'date': date, 'count': count})

        res = {
            'success': True,
            'message': 'Time series data successfully retrieved',
            'data': time_series_data
        }
        return res, 200


@main_app.route('/<string:short_name>')
@cache.cached(timeout=0)
def redirector(short_name):
    LOGGER.info(f"Url retrived from DB for short_name - {short_name}")
    self = ShortName()
    url_shortner = self.get_url_shortner(short_name=short_name)
    if not url_shortner:
        res = {
            'success': False,
            'message': 'url does not exist',
            'data': {},
        }
        return res, 404
    redirect_url = url_shortner.url
    if 'http' not in redirect_url or 'https' not in redirect_url:
        redirect_url = f'http://{redirect_url}'
    return redirect(redirect_url)


if __name__ == '__main__':
    main_app.run()
