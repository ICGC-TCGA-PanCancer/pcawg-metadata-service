from flask import current_app as capp
from es_query_builder import query_builder
import unicodedata

field_mapping = {
    'project': 'dcc_project_code',
    'submitter_donor_id': 'submitter_donor_id',
    'donor_unique_id': 'donor_unique_id',
    'normal_aligned': 'flags.is_normal_specimen_aligned',
    'tumor_aligned': 'flags.are_all_tumor_specimens_aligned',
    'variant_called': 'flags.variant_calling_performed',
    'blacklisted': 'flags.is_donor_blacklisted',
    'qc_failed': 'flags.is_manual_qc_failed',
    'tumor_count': 'flags.all_tumor_specimen_aliquot_counts',
    'normal_specimen_id': 'normal_alignment_status.submitter_specimen_id',
    'tumor_specimen_id': 'tumor_alignment_status.submitter_specimen_id',
}

def get_donor(request):
    search = request.args.get('search')
    search = unicodedata.normalize('NFKD', search).encode('ascii','ignore') if search else ''
    sort = request.args.get('sort')
    order = request.args.get('order') if request.args.get('order') == 'desc' else 'asc'
    limit = request.args.get('limit')
    offset = int(request.args.get('offset')) if request.args.get('offset') else 0

    es_sort = []
    if sort:
        es_sort = [
            {field_mapping.get(sort) if field_mapping.get(sort) else sort: {'order': order}}
        ]

    es_query = query_builder(search, field_mapping)
    es_query.update(
        {
            "fields": [
                "_id",
                field_mapping.get('project'),
                "donor_unique_id",
                "submitter_donor_id",
                field_mapping.get('normal_aligned'),
                field_mapping.get('tumor_aligned'),
                field_mapping.get('variant_called'),
                field_mapping.get('blacklisted'),
                field_mapping.get('qc_failed'),
                field_mapping.get('tumor_count'),
                field_mapping.get('normal_specimen_id'),
                field_mapping.get('tumor_specimen_id'),
                ],
            "size": limit,
            "from": offset,
            "sort": es_sort
        }
    )

    res = capp.es.search(
                            index = capp.config['ES_INDEX'], 
                            doc_type = 'donor',
                            body = es_query
                         )

    data = {'total': res['hits']['total'], 'rows': []}
    for hit in res['hits']['hits']:
        data['rows'].append({
            'donor_unique_id': hit['fields']['donor_unique_id'][0],
            'project': hit['fields'][field_mapping.get('project')][0],
            'submitter_donor_id': hit['fields']['submitter_donor_id'][0],
            'normal_aligned': hit['fields'][field_mapping.get('normal_aligned')][0],
            'tumor_aligned': hit['fields'][field_mapping.get('tumor_aligned')][0],
            'variant_called': hit['fields'][field_mapping.get('variant_called')] \
                              if hit['fields'].get(field_mapping.get('variant_called')) else [],
            'blacklisted': hit['fields'][field_mapping.get('blacklisted')][0],
            'qc_failed': hit['fields'][field_mapping.get('qc_failed')][0],
            'tumor_count': hit['fields'][field_mapping.get('tumor_count')][0],
            'normal_specimen_id': hit['fields'][field_mapping.get('normal_specimen_id')][0] \
                              if hit['fields'].get(field_mapping.get('normal_specimen_id')) else '',
            'tumor_specimen_id': hit['fields'][field_mapping.get('tumor_specimen_id')] \
                              if hit['fields'].get(field_mapping.get('tumor_specimen_id')) else [],
        })

    return data


