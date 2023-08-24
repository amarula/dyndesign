from dyndesign import ClassConfig, GlobalClassConfig
from ...samples.sample_builder_components import A, B


class BICConfigClass:
    GLOBAL_DYNCONFIG = GlobalClassConfig(
        injection_method='m1',
        add_components_after_method=True
    )

    option1 = (
        ClassConfig(inherit_from=A),
        ClassConfig(component_attr="comp", component_class=B)
    )
