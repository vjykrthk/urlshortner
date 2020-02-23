from app import ma


class UrlShortnerSchema(ma.ModelSchema):
    class Meta:
        fields = ("url", "short_name", "created_at", "updated_at")


url_shortner_schema = UrlShortnerSchema()
url_shortner_schema_multi = UrlShortnerSchema(many=True)
