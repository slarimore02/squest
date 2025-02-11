import logging

from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect
from django.template import Context
from django.template.loader import get_template
from django.urls import reverse
from django.utils.safestring import mark_safe
from graphviz import Digraph
from taggit.models import Tag

from resource_tracker.filters.graph_filter import GraphFilter
from resource_tracker.models import ResourceGroup, ResourcePool

logger = logging.getLogger(__name__)

COLORS = {'consumer': '#28a745', 'provider': '#dc3545', 'resource_pool': '#ff851b', 'resource_group': '#17a2b8',
          'available': '#ffc107', "green": "#28a745", "yellow": "#ffc107", "red": "#dc3545",
          'transparent': '#ffffff00', 'gray': '#6c757d'}


def get_graph_name(resource) -> str:
    '''
    Prefix ResourcePool's and ResouceGroup's name to prevent name collision in Graph
    :param resource: ResourcePool or ResourceGroup
    :return: str
    '''
    prefix = ''
    if isinstance(resource, ResourcePool):
        prefix = 'RP_'
    elif isinstance(resource, ResourceGroup):
        prefix = 'RG_'
    return f'{prefix}{resource.name}'.replace(':', '_')  # ':' is a special keyword in Dot


@user_passes_test(lambda u: u.is_superuser)
def resource_tracker_graph(request):
    dot = Digraph(comment='Graph')
    dot.attr(bgcolor=COLORS["transparent"])
    dot.name = 'Resource Tracker Graph'
    dot.attr('node', shape='plaintext')

    tags = Tag.objects.all()
    resource_graph_filtered = GraphFilter(request.GET, queryset=tags)
    display_graph = False

    tag_session_key = f'{request.path}__tags'

    tag_redirect_flag = "tag_redirect" in request.GET
    tags_from_session = request.session.get(tag_session_key, [])
    if len(tags_from_session) > 0 and not tag_redirect_flag:
        logger.info(f"Using tags loaded from session: {tags_from_session}")
        string_tag = "?"
        for tag in tags_from_session:
            string_tag += f"tag={tag}&"
        string_tag += "tag_redirect="  # in order to stop the redirect
        return redirect(reverse("resource_tracker:resource_tracker_graph") + string_tag)

    elif "tag" in request.GET:
        tag_list = request.GET.getlist("tag")
        resource_pool_queryset = ResourcePool.objects.filter(tags__name__in=tag_list)
        resource_group_queryset = ResourceGroup.objects.filter(tags__name__in=tag_list)
        logger.info(f"Settings tags from URL in session: {tag_list}")
        request.session[tag_session_key] = tag_list
    else:
        resource_pool_queryset = ResourcePool.objects.all()
        resource_group_queryset = ResourceGroup.objects.all()
        request.session[tag_session_key] = []

    for resource_pool in resource_pool_queryset:
        dot.node(f'{get_graph_name(resource_pool)}', label=create_resource_pool_svg(resource_pool))
        display_graph = True
    for resource_group in resource_group_queryset:
        display_graph = True
        dot.node(f'{get_graph_name(resource_group)}', label=create_resource_group_svg(resource_group))
        for attribute in resource_group.attribute_definitions.filter():
            rg = f'{get_graph_name(resource_group)}:{attribute.name}'
            if attribute.consume_from:
                dot.edge(f'{get_graph_name(attribute.consume_from.resource_pool)}:{attribute.consume_from.name}', rg,
                         color=COLORS['provider'])
            if attribute.produce_for:
                dot.edge(rg, f'{get_graph_name(attribute.produce_for.resource_pool)}:{attribute.produce_for.name}',
                         color=COLORS['consumer'])

    dot.format = 'svg'
    svg = mark_safe(dot.pipe().decode('utf-8'))

    return render(request, 'resource_tracking/graph/resource-tracker-graph.html',
                  context={'svg': svg,
                           'display_graph': display_graph,
                           'resource_graph': resource_graph_filtered})


def create_resource_pool_svg(resource_pool: ResourcePool):
    context = dict()
    context['name'] = {
        'display': resource_pool.name,
        'tooltip': f"Go to {resource_pool}",
        'href': reverse('resource_tracker:resource_pool_edit',
                        kwargs={'resource_pool_id': resource_pool.id})}

    context['attributes_list'] = [
        {
            'name': {
                'display': attribute.name,
                'tooltip': f"Go to {attribute}",
                'href': reverse('resource_tracker:resource_pool_attribute_edit',
                                kwargs={'resource_pool_id': resource_pool.id,
                                        'attribute_id': attribute.id})},
            'produced': {
                'display': round(attribute.total_produced),
                'tooltip': f"Go to {attribute}'s producers",
                'href': reverse(
                    'resource_tracker:resource_pool_attribute_producer_list',
                    kwargs={'resource_pool_id': resource_pool.id,
                            'attribute_id': attribute.id})},
            'consumed': {
                'display': f"{round(attribute.total_consumed)}",
                'color': COLORS[attribute.progress_bar_color],
                'tooltip': f"Go to {attribute}'s consumers",
                'href': reverse(
                    'resource_tracker:resource_pool_attribute_consumer_list',
                    kwargs={'resource_pool_id': resource_pool.id,
                            'attribute_id': attribute.id})},
            'available': {
                'display': f"{round(attribute.total_produced - attribute.total_consumed)}"
            },
            'percent': {
                'display': f"{attribute.percent_consumed}%",
                'color': COLORS[attribute.progress_bar_color],
                'tooltip': f"Go to {attribute}'s consumers",
                'href': reverse(
                    'resource_tracker:resource_pool_attribute_consumer_list',
                    kwargs={'resource_pool_id': resource_pool.id,
                            'attribute_id': attribute.id})
            }
        }
        for attribute in resource_pool.attribute_definitions.filter()]
    context['color'] = COLORS['resource_pool']
    context['color_available'] = COLORS['available']

    tm = get_template('resource_tracking/graph/resource_pool.j2').template
    return tm.render(context=Context(context))


def create_resource_group_svg(resource_group: ResourceGroup):
    context = dict()
    context['name'] = {
        'display': resource_group.name,
        'tooltip': f"Go to {resource_group}",
        'href': reverse('resource_tracker:resource_group_edit',
                        kwargs={'resource_group_id': resource_group.id})}
    context['count'] = {
        'display': resource_group.resources.count(),
        'tooltip': f"Go to {resource_group}'s resources",
        'href': reverse('resource_tracker:resource_group_resource_list',
                        kwargs={'resource_group_id': resource_group.id})}
    context['attributes_list'] = [
        {
            'key': attribute.name,
            'value': round(attribute.total_resource),
            'tooltip': f"Go to {attribute}",
            'href': reverse('resource_tracker:resource_group_attribute_edit',
                            kwargs={'resource_group_id': resource_group.id,
                                    'attribute_id': attribute.id})
        }
        for attribute in resource_group.attribute_definitions.filter()
    ]
    context['color'] = COLORS['resource_group']

    tm = get_template('resource_tracking/graph/resource_group.j2').template
    return tm.render(context=Context(context))
