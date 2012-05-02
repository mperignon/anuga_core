"""View results of runup_sinusoid.py
"""
#---------------
# Import Modules
#---------------
from anuga.utilities import plot_utils as util
from matplotlib import pyplot as pyplot
import numpy

p1=util.get_output('runup_sinusoid_v2.sww', 0.001)
p2=util.get_centroids(p1, velocity_extrapolation=True)

#------------------
# Select line
#------------------
#v=(p.y==0.5)
v=(p2.y==p2.y[80])

#--------------------
# Make plot animation
#--------------------
pyplot.close() #If the plot is open, there will be problems
pyplot.ion()

if True:
    line, = pyplot.plot( (p2.x[v].min(),p2.x[v].max()) ,(p2.xvel[:,v].min(),p2.xvel[:,v].max() ) )
    for i in range(p2.xmom.shape[0]):
        line.set_xdata(p2.x[v])
        line.set_ydata(p2.xvel[i,v])
        pyplot.draw()
        pyplot.plot( (0,1),(0,0), 'r' )
        pyplot.title(str(i)+'/200') # : velocity does not converge to zero' )
        pyplot.xlabel('x')
        pyplot.ylabel('Velocity (m/s)')

    pyplot.savefig('runup_x_velocities.png')


pyplot.clf()
# Plot vertex values

t1=numpy.argmin(abs(p1.time-1.0))
t2=len(p1.time)-1

pyplot.scatter(p1.x,p1.y,c=p1.elev,edgecolors='none', s=25)
pyplot.colorbar()
pyplot.quiver(p1.x,p1.y,p1.xvel[t1,:],p1.yvel[t1,:])
pyplot.title('The maximum VERTEX speed is '+ str(p1.vel[t1,:].max()) + ' m/s at time '+ str(p1.time[t1])+'s')
pyplot.savefig('vel_sinu3s_v2.png')

pyplot.clf()
# Plot vertex values
pyplot.scatter(p2.x,p2.y,c=p2.elev,edgecolors='none', s=25)
pyplot.colorbar()
pyplot.quiver(p2.x,p2.y,p2.xvel[t1,:],p2.yvel[t1,:])
pyplot.title('The maximum CENTROID speed is '+ str(p2.vel[t1,:].max()) + ' m/s at time ' + str(p1.time[t1]) + ' s')
pyplot.savefig('vel_sinu3s_v2_cent.png')

pyplot.clf()
# Plot vertex values
pyplot.scatter(p1.x,p1.y,c=p1.elev,edgecolors='none', s=25)
pyplot.colorbar()
pyplot.quiver(p1.x,p1.y,p1.xvel[t2,:],p1.yvel[t2,:])
pyplot.title('The maximum VERTEX speed is '+ str(p1.vel[t2,:].max()) + ' m/s at time ' + str(p1.time[t2]) +' s')
pyplot.savefig('vel_sinu30s_v2.png')

pyplot.clf()
# Plot vertex values
pyplot.scatter(p2.x,p2.y,c=p2.elev,edgecolors='none', s=25)
pyplot.colorbar()
pyplot.quiver(p2.x,p2.y,p2.xvel[t2,:],p2.yvel[t2,:])
pyplot.title('The maximum CENTROID speed is '+ str(p2.vel[t2,:].max()) + ' m/s at time' + str(p1.time[t2])+ ' s')
pyplot.savefig('vel_sinu30s_v2_cent.png')

