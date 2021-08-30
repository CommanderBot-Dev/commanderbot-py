from string import Formatter

__all__ = ("ShallowFormatter",)


class ShallowFormatter(Formatter):
    """
    A string template formatter that only accepts flat values as arguments.

    This can be used as a type of "safe" formatter with untrusted input, so long as all
    of the arguments passed to it are themselves safe.

    Any field access will result in a `ValueError`.
    """

    def get_field(self, field_name, args, kwargs):
        # Instead of doing any string parsing ourselves, we simply check whether the
        # final object returned by the default (superclass) implementation is the same
        # as the root object we started with. If this is not the case, then some type of
        # field access must have occured and therefore the argument is invalid.
        final_obj, first = super().get_field(field_name, args, kwargs)
        root_obj = self.get_value(first, args, kwargs)
        if final_obj != root_obj:
            raise ValueError(f"Invalid string template argument: {field_name}")
        return root_obj, first
