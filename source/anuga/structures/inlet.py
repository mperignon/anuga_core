import anuga.geometry.polygon
from anuga.geometry.polygon import inside_polygon, is_inside_polygon, line_intersect
from anuga.config import velocity_protection, g
from anuga import Region

import math


import numpy as num

class Inlet:
    """Contains information associated with each inlet
    """

    def __init__(self, domain, poly, verbose=False):

        self.domain = domain
        self.domain_bounding_polygon = self.domain.get_boundary_polygon()
        self.poly = num.asarray(poly, dtype=num.float64)
        self.verbose = verbose
        
        
        # poly can be either a line, polygon or a regions
        if isinstance(poly,Region):
            #print "is region"
            self.region = poly
        else:
            self.region = Region(domain,poly=poly,expand_polygon=True)
            #print 'is line or polygon'

        
        #self.line = True
        #if len(self.poly) > 2:
        #    self.line = False

        self.triangle_indices = self.region.indices

        #print self.triangle_indices
        #print poly
        #print self.triangle_indices
        
        #self.compute_triangle_indices()
        self.compute_area()
        #self.compute_inlet_length()



    ## def compute_triangle_indices(self):

    ##     # Get boundary (in absolute coordinates)
    ##     bounding_polygon = self.domain_bounding_polygon
    ##     domain_centroids = self.domain.get_centroid_coordinates(absolute=True)
    ##     vertex_coordinates = self.domain.get_vertex_coordinates(absolute=True)

    ##     if self.line: # poly is a line
    ##         # Check that line lies within the mesh.
    ##         for point in self.poly:
    ##             msg = 'Point %s ' %  str(point)
    ##             msg += ' did not fall within the domain boundary.'
    ##             assert is_inside_polygon(point, bounding_polygon), msg
                
    ##         self.triangle_indices = line_intersect(vertex_coordinates, self.poly)

    ##     else: # poly is a polygon

    ##         tris_0 = line_intersect(vertex_coordinates, [self.poly[0],self.poly[1]])
    ##         tris_1 = inside_polygon(domain_centroids, self.poly)
    ##         #print 40*"="
    ##         #print tris_0
    ##         #print tris_1
    ##         self.triangle_indices = num.union1d(tris_0, tris_1)
    ##         #print self.triangle_indices

    ##     if len(self.triangle_indices) == 0:
    ##         msg = 'Inlet poly=%s ' % (self.poly)
    ##         msg += 'No triangle centroids intersecting poly '
    ##         raise Exception, msg




    def compute_area(self):
        
        # Compute inlet area as the sum of areas of triangles identified
        # by line. Must be called after compute_inlet_triangle_indices().
        if len(self.triangle_indices) == 0:
            region = 'Inlet line=%s' % (self.inlet_line)
            msg = 'No triangles have been identified in region '
            raise Exception, msg
        
#        self.area = 0.0
#        for j in self.triangle_indices:
#            self.area += self.domain.areas[j]

        self.area = num.sum(self.domain.areas[self.triangle_indices])

        msg = 'Inlet exchange area has area = %f' % self.area
        assert self.area > 0.0


#    def compute_inlet_length(self):
#        """ Compute the length of the inlet (as
#        defined by the input line
#        """
#
#        self.inlet_length = anuga.geometry.polygon.line_length(self.poly)


#    def get_inlet_length(self):
#
#        return self.inlet_length



    def get_poly(self):

        return self.poly
        
    def get_area(self):

        return self.area

    
    def get_areas(self):
        
        # Must be called after compute_inlet_triangle_indices().
        return self.domain.areas.take(self.triangle_indices)
    
        
    def get_stages(self):
        
        return self.domain.quantities['stage'].centroid_values.take(self.triangle_indices)
        
        
    def get_average_stage(self):

        return num.sum(self.get_stages()*self.get_areas())/self.area
        
    def get_elevations(self):    
        
        return self.domain.quantities['elevation'].centroid_values.take(self.triangle_indices)
        
    def get_average_elevation(self):

        return num.sum(self.get_elevations()*self.get_areas())/self.area
    
    
    def get_xmoms(self):
    
        return self.domain.quantities['xmomentum'].centroid_values.take(self.triangle_indices)
        
        
    def get_average_xmom(self):

        return num.sum(self.get_xmoms()*self.get_areas())/self.area
        
    
    def get_ymoms(self):
        
        return self.domain.quantities['ymomentum'].centroid_values.take(self.triangle_indices)
 
 
    def get_average_ymom(self):
        
        return num.sum(self.get_ymoms()*self.get_areas())/self.area
    

    def get_depths(self):
    
        return self.get_stages() - self.get_elevations()
    
    
    def get_total_water_volume(self):
       
       return num.sum(self.get_depths()*self.get_areas())
  

    def get_average_depth(self):
    
        return self.get_total_water_volume()/self.area
        
        
    def get_velocities(self):
        
            depths = self.get_depths()
            u = self.get_xmoms()/(depths + velocity_protection/depths)
            v = self.get_ymoms()/(depths + velocity_protection/depths)
            
            return u, v


    def get_xvelocities(self):

            depths = self.get_depths()
            return self.get_xmoms()/(depths + velocity_protection/depths)

    def get_yvelocities(self):

            depths = self.get_depths()
            return self.get_ymoms()/(depths + velocity_protection/depths)
            
            
    def get_average_speed(self):
 
            u, v = self.get_velocities()
            
            average_u = num.sum(u*self.get_areas())/self.area
            average_v = num.sum(v*self.get_areas())/self.area
            
            return math.sqrt(average_u**2 + average_v**2)


    def get_average_velocity_head(self):

        return 0.5*self.get_average_speed()**2/g


    def get_average_total_energy(self):
        
        return self.get_average_velocity_head() + self.get_average_stage()
        
    
    def get_average_specific_energy(self):
        
        return self.get_average_velocity_head() + self.get_average_depth()



    def set_depths(self,depth):

        self.domain.quantities['stage'].centroid_values.put(self.triangle_indices, self.get_elevations() + depth)


    def set_stages(self,stage):

        self.domain.quantities['stage'].centroid_values.put(self.triangle_indices, stage)


    def set_xmoms(self,xmom):

        self.domain.quantities['xmomentum'].centroid_values.put(self.triangle_indices, xmom)


    def set_ymoms(self,ymom):

        self.domain.quantities['ymomentum'].centroid_values.put(self.triangle_indices, ymom)


    def set_elevations(self,elevation):

        self.domain.quantities['elevation'].centroid_values.put(self.triangle_indices, elevation)

    def set_stages_evenly(self,volume):
        """ Distribute volume of water over
        inlet exchange region so that stage is level
        """

        areas = self.get_areas()
        stages = self.get_stages()
        depths = self.get_depths()

        stages_order = stages.argsort()

        # accumulate areas of cells ordered by stage
        summed_areas = num.cumsum(areas[stages_order])
        
        # accumulate the volume need to fill cells
        summed_volume = num.zeros_like(areas)       
        summed_volume[1:] = num.cumsum(summed_areas[:-1]*num.diff(stages[stages_order]))


        assert volume >= 0.0


        index = num.nonzero(summed_volume<=volume)[0][-1]

        # calculate stage needed to fill chosen cells with given volume of water
        depth = (volume - summed_volume[index])/summed_areas[index]
        stages[stages_order[0:index+1]] = stages[stages_order[index]]+depth

        self.set_stages(stages)




    def set_depths_evenly(self,volume):
        """ Distribute volume over all exchange
        cells with equal depth of water
        """
	    
        new_depth = self.get_average_depth() + (volume/self.get_area())
        self.set_depths(new_depth)

