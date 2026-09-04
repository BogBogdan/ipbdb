# -*- coding: utf-8 -*-
#
# Picks the plot type of a TabulatedData set from the shape of its values:
# surface, waterfall, curve_theta, curve_e, invalid
#

KIND_LABELS = {
    'surface': '3D surface',
    'waterfall': '3D waterfall',
    'curve_theta': '2D DCS(theta)',
    'curve_e': '2D sigma(E)',
    'invalid': 'invalid data',
}


def normalize(parameter):
    name = (parameter or '').strip().lower()
    if 'loss' in name:
        return 'energy-loss'
    if 'angle' in name:
        return 'angle'
    if 'energy' in name:
        return 'energy'
    if name in ('err', 'error', 'accuracy'):
        return 'error'
    return name


def raw_text(datalist):
    if datalist is None:
        return ''
    return datalist.data_values or ''


def wrong_separator(datalist):
    # some rows were pasted from excel
    text = raw_text(datalist)
    return ',' in text or ';' in text or '\t' in text


def split_tokens(datalist):
    text = raw_text(datalist)
    for separator in (',', ';', '\t'):
        text = text.replace(separator, ' ')
    return text.split()


def split_values(datalist):
    numbers = []
    for token in split_tokens(datalist):
        try:
            numbers.append(float(token))
        except ValueError:
            pass
    return numbers


def get_axes(tabdata):
    energy = angle = y = error = None
    for datalist in tabdata.x.all():
        name = normalize(datalist.parameter)
        if name == 'energy' and energy is None:
            energy = datalist
        elif name == 'angle' and angle is None:
            angle = datalist
    for datalist in tabdata.y.all():
        if normalize(datalist.parameter) == 'error':
            error = error or datalist
        elif y is None:
            y = datalist
    for datalist in tabdata.accuracy.all():
        error = datalist
        break
    if y is None:
        # a few sets keep the cross section on the x side
        for datalist in tabdata.x.all():
            if normalize(datalist.parameter) not in ('energy', 'angle', 'error'):
                y = datalist
                break
    return energy, angle, y, error


def find_problems(energy, angle, y, error):
    # fatal stops the plot, warnings are only reported
    fatal = []
    warnings = []

    for datalist, label in ((energy, 'energy'), (angle, 'angle'), (y, 'y')):
        values = split_values(datalist)
        skipped = len(split_tokens(datalist)) - len(values)
        if skipped:
            fatal.append('%d values on the %s axis cannot be read' % (skipped, label))
        if datalist and datalist.count is not None and values \
                and datalist.count != len(values):
            fatal.append('count field says %s but the %s axis has %d values'
                         % (datalist.count, label, len(values)))
        if wrong_separator(datalist):
            warnings.append('%s axis uses commas or tabs instead of spaces, ignored'
                            % label)

    n_energy = len(split_values(energy))
    n_angle = len(split_values(angle))
    n_y = len(split_values(y))
    n_error = len(split_values(error))

    if not n_energy:
        fatal.append('no energy axis')
    if not n_y:
        fatal.append('no cross section values')
    if n_energy and n_y and n_energy != n_y:
        fatal.append('y has %d values and the energy axis has %d' % (n_y, n_energy))
    if n_energy and n_angle and n_energy != n_angle:
        fatal.append('angle axis has %d values and the energy axis has %d'
                     % (n_angle, n_energy))
    if n_error and n_y and n_error != n_y:
        warnings.append('error has %d values and y has %d, ignored' % (n_error, n_y))
    return fatal, warnings


def find_extra_lists(tabdata):
    # a set should carry one energy axis, one angle axis and one cross section
    warnings = []
    axes = [normalize(d.parameter) for d in tabdata.x.all()]
    for name in ('energy', 'angle'):
        if axes.count(name) > 1:
            warnings.append('%d %s axes are linked, only the first one is used'
                            % (axes.count(name), name))
    values = [d for d in tabdata.y.all() if normalize(d.parameter) != 'error']
    if len(values) > 1:
        warnings.append('%d cross sections are linked, only the first one is used'
                        % len(values))
    strange = [d.parameter for d in tabdata.x.all()
               if normalize(d.parameter) not in ('energy', 'angle', 'energy-loss')]
    if strange:
        warnings.append('%s is linked as an axis' % ', '.join(strange))
    return warnings


def group_by_energy(energies, angles, values, errors):
    series = {}
    for index, energy in enumerate(energies):
        item = series.setdefault(energy, {'energy': energy, 'angle': [],
                                          'y': [], 'error': []})
        item['angle'].append(angles[index])
        item['y'].append(values[index])
        item['error'].append(errors[index] if index < len(errors) else None)

    result = [series[energy] for energy in sorted(series)]
    for item in result:
        points = sorted(zip(item['angle'], item['y'], item['error']),
                        key=lambda point: point[0])
        item['angle'] = [point[0] for point in points]
        item['y'] = [point[1] for point in points]
        item['error'] = [point[2] for point in points]
    return result


def prepare(tabdata):
    energy, angle, y, error = get_axes(tabdata)
    fatal, warnings = find_problems(energy, angle, y, error)
    warnings += find_extra_lists(tabdata)

    energies = split_values(energy)
    angles = split_values(angle)
    values = split_values(y)
    errors = split_values(error)
    if len(errors) != len(values):
        errors = []

    collision = tabdata.dataset.collision if tabdata.dataset else None
    meta = {
        'id': tabdata.id,
        'description': tabdata.description or '',
        'cs_type': tabdata.cross_section_type.code or tabdata.cross_section_type.name,
        'cs_name': tabdata.cross_section_type.name,
        'collision_type': collision.collision_type.name if collision else '',
        'target': collision.reactant.species.name if collision else '',
        'target_formula': collision.reactant.species.chemical_formula if collision else '',
        'product': collision.product.species.name if collision else '',
        'product_formula': collision.product.species.chemical_formula if collision else '',
        'product_state': state_label(collision.product) if collision else '',
        'sources': [source.source_id for source in tabdata.dataset.sources.all()]
                   if tabdata.dataset else [],
        'unit_energy': (energy.unit if energy else '') or 'eV',
        'unit_angle': (angle.unit if angle else '') or 'deg',
        'unit_y': (y.unit if y else '') or '',
        'n_points': len(values),
        'n_energies': len(set(energies)),
        'n_angles': len(set(angles)),
        'problems': fatal + warnings,
        'series': [],
    }

    if fatal:
        meta['kind'] = 'invalid'
        return meta

    if not angles:
        points = sorted(zip(energies, values,
                            errors + [None] * (len(values) - len(errors))),
                        key=lambda point: point[0])
        meta['kind'] = 'curve_e'
        meta['series'] = [{'energy': None,
                           'x': [point[0] for point in points],
                           'y': [point[1] for point in points],
                           'error': [point[2] for point in points]}]
        return meta

    meta['series'] = group_by_energy(energies, angles, values, errors)
    angle_sets = set(tuple(item['angle']) for item in meta['series'])
    if len(meta['series']) == 1:
        meta['kind'] = 'curve_theta'
    elif len(angle_sets) == 1:
        meta['kind'] = 'surface'
        meta['angles'] = list(angle_sets.pop())
        meta['energies'] = [item['energy'] for item in meta['series']]
        meta['z'] = [item['y'] for item in meta['series']]
    else:
        meta['kind'] = 'waterfall'
    return meta


def state_label(state):
    return state.term or state.description or state.configuration or ''


def title(meta):
    parts = [meta['target_formula'] or meta['target'], meta['collision_type'],
             meta['product_state'], meta['cs_name']]
    return ' - '.join(part for part in parts if part)
