from . models import OrganizationalStructureOfficeEmployee


def user_in_office(user, office_slug_list=[], structure=None):
    if not office_slug_list: return False
    osoe = OrganizationalStructureOfficeEmployee
    employees = osoe.objects.filter(employee=user,
                                    office__is_active=True,
                                    office__slug__in=office_slug_list,
                                    office__organizational_structure__is_active=True)
    if structure:
        employees = employees.filter(office__organizational_structure=structure)
    return employees.exists()


def user_office_structures(user, office_slug_list=[]):
    if not office_slug_list: return False
    osoe = OrganizationalStructureOfficeEmployee
    structures = osoe.objects.select_related('office__organizational_structure')\
                             .filter(employee=user,
                                     office__is_active=True,
                                     office__slug__in=office_slug_list,
                                     office__organizational_structure__is_active=True)\
                             .values_list('office__organizational_structure', flat=True)
    return structures
