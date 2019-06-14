import bpy
import json
from . exporters import transform

def write_json(context, filepath, object, animType, id, looping, resetWhenDone):
    # identify correct export type and get frames
    if animType == 'TRANSFORM':
        frames = transform.write_animation(context, object, id, looping, resetWhenDone)
        typeLabel = "transform"
    else:
        print("Unknown animation type "+animType)

    # add metadata
    animation = {
        "name":"remove this slot",
        "type":typeLabel,
        "id":id,
        "looping":looping,
        "resetWhenDone":resetWhenDone,
        "frames":frames,
        "commands":[]
    }

    # create json string
    formatted = json.dumps(animation, sort_keys=True, indent=4, separators=(',', ': '))

    # write file
    file = open(filepath, 'w')
    file.write(formatted)
    file.close

    print("Wrote to "+filepath)
    return {'FINISHED'}

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class MC_Export_Operator(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "mcanim.export_anim"  # important since its how bpy.ops.import_test.some_data is constructed
    bl_label = "Export Minecraft Animation"

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    filter_glob: StringProperty(
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,  # Max internal buffer length, longer would be clamped. 
    )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    animType = EnumProperty(
        name="Type",
        description="Animation type to export",
        items={('TRANSFORM','Transform', 'Basic transform animation (no roll)')},
        default='TRANSFORM'
    )

    looping = BoolProperty(
        name="Looping",
        description="Should this animation loop?",
        default=True,
        )

    resetWhenDone = BoolProperty(
        name="Reset when done",
        description="Should this reset to starting position when done?",
        default=False,
        )

    id = StringProperty(
        name="ID",
        description="Unique numerical ID that Minecraft will refer to this animation by",
        default='0',
        )

    def execute(self, context):
        return write_json(context, self.filepath, context.view_layer.objects.active, self.animType, int(self.id), self.looping, self.resetWhenDone)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(MC_Export_Operator.bl_idname, text="Minecraft Animation (.json)")


def register():
    print("registering anim export")
    bpy.utils.register_class(MC_Export_Operator)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(MC_Export_Operator)
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.export_test.some_data('INVOKE_DEFAULT')
