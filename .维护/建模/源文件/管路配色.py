# coding: utf-8
"""Shared diagram and assembly-finish palette. Display choices only."""
def rgb(hex_value):
    return [int(hex_value[i:i+2],16)/255 for i in (1,3,5)]

PALETTE={
 'Return':{'hex':'#168966','name':'绿色｜上水20'},
 'DrainMain':{'hex':'#2478b5','name':'蓝色｜主下水25'},
 'DrainEmergency':{'hex':'#ce741b','name':'橙色｜独立应急25'},
 'ATO':{'hex':'#9255b6','name':'紫色｜自动补水'},
}
HANDLES={'GateHandwheel','ReturnIsolationHandle','ReturnFrontValveHandle','ReturnRearValveHandle'}
PHYSICAL_PALETTE={'Return':'#b4bdc4','DrainMain':'#796291','DrainEmergency':'#796291','fittings':'#737b83'}

def apply_route_colors(styles):
    colored={}
    for name,style in styles.items():
        group=style.get('group')
        if name=='SightStraightSpare':group='DrainMain'
        if group not in PALETTE:continue
        if name.startswith(('Clip','Liner')):continue
        if group=='ATO' and name not in ['PipeATO','ATOBreak','ATOSensor']:continue
        style['circuit']=group
        if name in HANDLES:
            style['color']=rgb('#b81f29')
        elif name=='ReturnCheckFlap':
            style['color']=rgb('#424b52')
        else:
            style['color']=rgb(PALETTE[group]['hex'])
        if style.get('clear_spool'):style['alpha']=55
        colored[name]=group
    return colored

def assembly_finish(styles):
    """Return a preview only; the saved CAD continues to use circuit colours."""
    import copy
    finish=copy.deepcopy(styles)
    for name,style in finish.items():
        group=style.get('group')
        if group in ['DrainMain','DrainEmergency','Return'] or name=='SightStraightSpare':
            if name.startswith(('Clip','Liner')):continue
            style['color']=rgb(PHYSICAL_PALETTE['fittings'])
            style['alpha']=0
            # Colour only the continuous pipe runs. Service fittings share a dark finish.
            if name.startswith(('Pipe','Standpipe')) or name=='SightStraightSpare':
                circuit='DrainMain' if name=='SightStraightSpare' else group
                style['color']=rgb(PHYSICAL_PALETTE[circuit])
                if name.startswith('Pipe') and group in ['DrainMain','DrainEmergency']:
                    style['colour_straights_only']=True
        if name in HANDLES:style['color']=rgb('#b81f29')
    # Five user-confirmed removable clear pipes, plus the existing sight.
    for style in finish.values():
        if style.get("clear_spool"):style.update(color=rgb("#c3e1e8"),alpha=65)
    # Equipment windows remain local transparent components.
    finish['SightWindow'].update(color=rgb('#c3e1e8'),alpha=65)
    finish['SightRotor'].update(color=rgb('#c5202c'),alpha=0)
    finish['ReturnCheckBody'].update(color=rgb('#c3e1e8'),alpha=65)
    finish['ReturnCheckFlap'].update(color=rgb('#495058'),alpha=0)
    finish['PumpSoftLink'].update(color=rgb('#20262a'),alpha=0)
    # A short translucent OEM ATO hose makes tiny bubbles/priming visible.
    for name in ['PipeATO','ATOBreak','ATOSensor']:
        finish[name].update(color=rgb('#d0d8df') if name=='PipeATO' else rgb('#343b42'),alpha=20 if name=='PipeATO' else 0)
    return finish

def apply_physical_surface_colours(obj,style):
    # Swept pipe geometry includes elbow bodies; only straight stock has custom colours.
    if style.get('colour_straights_only'):
        fitting=rgb(PHYSICAL_PALETTE['fittings'])
        obj.ViewObject.DiffuseColor=[tuple(style['color'] if type(face.Surface).__name__=='Cylinder' else fitting) for face in obj.Shape.Faces]
