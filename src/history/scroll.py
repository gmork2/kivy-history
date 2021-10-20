from enum import Enum, unique


"""
Allows web applications to explicitly set default scroll restoration
behavior on history navigation. This property can be either auto or
manual.

:Options:
    'auto':
        The location on the page to which the user has scrolled will be
        restored.
    'manual': The location on the page is not restored, The user will have
        to scroll to the location manually.
"""
ScrollRestoration = unique(Enum('ScrollRestoration', 'auto manual'))
