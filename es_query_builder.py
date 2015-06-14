from copy import deepcopy
import re
import pprint

query_template = {
  "query": {
    "bool": {
      "should": [
        {
          "query_string": {
            "query": "*"
          }
        }
      ]
    }
  }
}

def parse_query_string(search_str, field_mapping):
    if not search_str: return ([], {})

    # split on space first
    parts = search_str.split(' ')

    keywords = set()
    field_matches = {}
    for part in parts:
        if not part: continue

        if not '=' in part: # has no '='
            keywords = keywords.union(set(part.split(',')))
        else:
            field, value = part.split('=', 1)

            if not field_mapping.get(field):  # unknown field, still treat as keyword
                keywords = keywords.union(set(part.split(',')))
                continue

            if not field_matches.get(field_mapping.get(field)):
                field_matches[field_mapping.get(field)] = set()

            field_matches[field_mapping.get(field)] = field_matches[field_mapping.get(field)].union(set(value.split(',')))

    return keywords, field_matches


def build_should_clause(keywords, field_mapping):
    es_fields = set()
    for f in field_mapping: es_fields.add(field_mapping.get(f))

    prefixes = set()
    terms = set()
    for k in keywords:
        if k.endswith('*'):
            k = k.rstrip('*')
            if k == '': continue
            prefixes.add(k)
        else:
            terms.add(k)

    should_clause = []
    for f in es_fields:
        if not f in (
            'dcc_project_code',
            'donor_unique_id',
            'submitter_donor_id',
            'normal_alignment_status.submitter_specimen_id',
            'tumor_alignment_status.submitter_specimen_id',
            'flags.variant_calling_performed',
          ): continue

        if terms: should_clause.append(
            {
                "terms": {
                    f: list(terms)
                }
            }
        )

        if prefixes: should_clause.append(
            {
                "prefix": {
                    f: list(prefixes)
                }
            }
        )

    return should_clause


def build_must_clause(field_matches):

    prefixes = {}
    terms = {}
    for f in field_matches:
        new_prefixes_v = set()
        new_terms_v = set()
        for v in field_matches.get(f):
          if v.endswith('*'):
              v = v.rstrip('*')
              if v == '': continue
              new_prefixes_v = new_prefixes_v.union(set([v]))
          else:
              new_terms_v = new_terms_v.union(set([v]))

        if new_prefixes_v: prefixes.update({f: list(new_prefixes_v)})
        if new_terms_v: terms.update({f: list(new_terms_v)})

    must_clause = []
    for f in terms:
        must_clause.append( { "terms": { f: terms.get(f) } } )

    for f in prefixes:
        must_clause.append( { "prefix": { f: prefixes.get(f) } } )

    return must_clause


def query_builder(search_str, field_mapping):
    # parse search_str
    keywords, field_matches = parse_query_string(search_str, field_mapping)

    '''
    print 'keywords:'
    print keywords
    print 'field_matches'
    print field_matches
    '''

    should_clause = build_should_clause(keywords, field_mapping)
    #pprint.pprint(should_clause)
    must_clause = build_must_clause(field_matches)
    #pprint.pprint(must_clause)

    query = deepcopy(query_template)
    query.update({
        "filter": {
            "bool": {
                "should": should_clause,
                "must": must_clause
            }
        }
    })

    return query

