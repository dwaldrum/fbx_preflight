# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
from . import addon_updater_ops
from . import helpers

LARGE_BUTTON_SCALE_Y = 1.5


class PreflightPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Pre-Flight FBX"
    bl_context = "objectmode"
    bl_category = "Pre-Flight FBX"

    def draw(self, context):
        layout = self.layout
        groups = context.scene.preflight_props.fbx_export_groups

        # Export Groups
        layout.operator(
            "preflight.add_export_group",
            text="Add Export Group",
            icon="ZOOMIN")

        for group_idx, group in enumerate(groups):
            self.layout_export_group(group_idx, group, layout, context)

        layout.separator()

        # Export Button
        export_row = layout.row()
        export_row.scale_y = LARGE_BUTTON_SCALE_Y
        exportButton = export_row.operator("preflight.export_groups", icon="EXPORT")
        layout.separator()

    def layout_export_group(self, group_idx, group, layout, context):
        group_box = layout.box()

        # Header Row
        self.layout_header(group_box, group, group_idx)

        if group.is_collapsed is False:
            # Mesh Collection
            self.layout_object_list(group_box, group, group_idx)

            if group.obj_idx is not None and len(
                    group.obj_names) > group.obj_idx:
                selected_obj = group.obj_names[group.obj_idx]
                group_box.prop_search(
                    selected_obj,
                    "obj_name",
                    context.scene,
                    "objects",
                    text="")

            # Export Options
            options_column = group_box.column(align=True)
            options_column.prop(group, "include_animations")
            options_column.prop(group, "apply_modifiers")

    def layout_object_list(self, layout, group, group_idx):
        obj_list_row = layout.row()
        obj_list_row.template_list("ExportObjectUIList", "obj_list", group,
                                   "obj_names", group, "obj_idx")

        obj_list_actions_col = obj_list_row.column(align=True)

        add_obj_button = obj_list_actions_col.operator(
            "preflight.add_object_to_group", text="", icon="ZOOMIN")
        add_obj_button.group_idx = group_idx

        remove_obj_button = obj_list_actions_col.operator(
            "preflight.remove_object_from_group", text="", icon="ZOOMOUT")
        remove_obj_button.group_idx = group_idx
        remove_obj_button.object_idx = group.obj_idx

    def layout_header(self, layout, group, group_idx):
        header_row = layout.row()

        collapse_icon = "TRIA_RIGHT" if group.is_collapsed else "TRIA_DOWN"
        header_row.prop(
            group,
            "is_collapsed",
            icon=collapse_icon,
            icon_only=True,
            emboss=False)

        header_row.alert = not helpers.group_is_valid(group)
        header_row.prop(group, "name", text="")
        header_row.alert = False

        header_row.operator(
            "preflight.remove_export_group", icon="X", text="",
            emboss=False).group_idx = group_idx


class PreflightPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    # addon updater preferences

    auto_check_update = bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False)
    updater_intrval_months = bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0)
    updater_intrval_days = bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0)
    updater_intrval_hours = bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23)
    updater_intrval_minutes = bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59)

    def draw(self, context):
        layout = self.layout

        # updater draw function
        addon_updater_ops.update_settings_ui(self, context)


class PreflightExportOptionsPanel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_label = "Export Options"
    bl_context = "objectmode"
    bl_category = "Pre-Flight FBX"

    def draw(self, context):
        layout = self.layout
        export_options = context.scene.preflight_props.export_options

        layout.label("Export Location", icon="LIBRARY_DATA_DIRECT")
        layout.prop(export_options, "export_location", text="")
        layout.separator()
        layout.label("Export Types", icon="EXPORT")
        layout.prop(export_options, "object_types")
        layout.separator()
        layout.prop(export_options, "axis_up")
        layout.prop(export_options, "axis_forward")
        layout.separator()
        layout.label("Animation Options", icon="ARMATURE_DATA")
        layout.prop(export_options, "bake_anim_step")
        layout.prop(export_options, "bake_anim_simplify_factor")
        layout.prop(export_options, "use_anim")
        layout.prop(export_options, "separate_animations")
        layout.separator()
        layout.operator("preflight.reset_export_options")

