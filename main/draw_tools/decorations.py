import seaborn as sns
import matplotlib.pyplot as plt

def b2helix(n):
    return sns.cubehelix_palette(n, start=1.5, rot=1.5, dark=0.3, light=.8, reverse=True)
def watermark(t=None,logo="Belle II", px=0.033, py=0.915, fontsize=16, alpha=0.8, alpha_logo=0.95, shift=0.15, bstyle='italic', *args, **kwargs):
       
    """

    Args:
        t:
        logo:
        px:
        py:
        fontsize:
        alpha:
        shift:
        *args:
        **kwargs:

    Returns:

    """
    if t is None:
        import datetime
        t = " %d (group)" % datetime.date.today().year

    plt.text(px, py, logo, ha='left',
             transform=plt.gca().transAxes,
             fontsize=fontsize,
             style=bstyle,
             alpha=alpha_logo,
             weight='bold',
             *args, **kwargs,
             # fontproperties=font,
             # bbox={'facecolor':'#377eb7', 'alpha':0.1, 'pad':10}
             )
    plt.text(px + shift, py, t, ha='left',
             transform=plt.gca().transAxes,
             fontsize=fontsize,
             #          style='italic',
             alpha=alpha,  *args, **kwargs
             #          fontproperties=font,
             # bbox={'facecolor':'#377eb7', 'alpha':0.1, 'pad':10}
             )  
