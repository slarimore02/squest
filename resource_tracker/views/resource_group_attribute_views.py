from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404

from resource_tracker.forms import ResourceGroupAttributeDefinitionForm
from resource_tracker.models import ResourceGroup, ResourceGroupAttributeDefinition


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_create(request, resource_group_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    if request.method == 'POST':
        form = ResourceGroupAttributeDefinitionForm(request.POST)
        form.resource_group = resource_group  # give the resource_group so the form can validate the unique together
        if form.is_valid():
            new_attribute = form.save()
            new_attribute.resource_group_definition = resource_group
            new_attribute.save()
            from resource_tracker.views import resource_group_edit
            return redirect(resource_group_edit, resource_group.id)
    else:
        form = ResourceGroupAttributeDefinitionForm()

    return render(request,
                  'resource_tracking/resource_group/attributes/attribute-create.html',
                  {'form': form, 'resource_group': resource_group})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_edit(request, resource_group_id, attribute_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    attribute = get_object_or_404(ResourceGroupAttributeDefinition, id=attribute_id)
    form = ResourceGroupAttributeDefinitionForm(request.POST or None, instance=attribute)
    if form.is_valid():
        form.save()
        from resource_tracker.views import resource_group_edit
        return redirect(resource_group_edit, resource_group.id)
    return render(request, 'resource_tracking/resource_group/attributes/attribute-edit.html',
                  {'form': form, 'attribute': attribute, 'resource_group': resource_group})


@user_passes_test(lambda u: u.is_superuser)
def resource_group_attribute_delete(request, resource_group_id, attribute_id):
    resource_group = get_object_or_404(ResourceGroup, id=resource_group_id)
    attribute = get_object_or_404(ResourceGroupAttributeDefinition, id=attribute_id)
    if request.method == "POST":
        attribute.delete()
        from resource_tracker.views import resource_group_edit
        return redirect(resource_group_edit, resource_group.id)
    context = {
        "resource_group": resource_group,
        "attribute": attribute
    }
    return render(request, "resource_tracking/resource_group/attributes/attribute-delete.html", context)