# Your Agent for solving Raven's Progressive Matrices. You MUST modify this file.
#
# You may also create and submit new files in addition to modifying this file.
#
# Make sure your file retains methods with the signatures:
# def __init__(self)
# def Solve(self,problem)
#
# These methods will be necessary for the project's main method to run.

# Install Pillow and uncomment this line to access image processing.
#from PIL import Image
import numpy as np
from PIL import Image, ImageChops as Chops, ImageFilter as Filter
import os
import sys
import time
import math

class Agent:
    # The default constructor for your Agent. Make sure to execute any
    # processing necessary before your Agent starts solving problems here.
    #
    # Do not add any variables to this signature; they will not be used by
    # main().
    def __init__(self):
        pass

    # The primary method for solving incoming Raven's Progressive Matrices.
    # For each problem, your Agent's Solve() method will be called. At the
    # conclusion of Solve(), your Agent should return an int representing its
    # answer to the question: 1, 2, 3, 4, 5, or 6. Strings of these ints 
    # are also the Names of the individual RavensFigures, obtained through
    # RavensFigure.getName(). Return a negative number to skip a problem.
    #
    # Make sure to return your answer *as an integer* at the end of Solve().
    # Returning your answer as a string may cause your program to crash.

    def Solve(self,problem):

        ##############################
        ##
        ## Finding the rule of transforming one object to another
        ##
        ##############################

        def generate_transformation_rules(object1, object2):

            rule = {}
            sizes_list = ['very small', 'small', 'medium', 'large', 'very large', 'huge']

            if ('size' in object1.attributes) and ('size' in object2.attributes):
                object1_size_value = sizes_list.index(object1.attributes['size'])
                object2_size_value = sizes_list.index(object2.attributes['size'])
                rule['size'] = object1_size_value - object2_size_value
            else:
                rule['size'] = 'NA'

            if ('angle' in object1.attributes) and ('angle' in object2.attributes):
                if object1.attributes['angle'] == object2.attributes['angle']:
                    rule['angle'] = 'identical'
                else:
                    rule['angle'] = str(object1.attributes['angle']) + "_" + str(object2.attributes['angle'])
            else:
                rule['angle'] = 'NA'

            if ('alignment' in object1.attributes) and ('alignment' in object2.attributes):
                rule['alignment'] = object1.attributes['alignment'] + "_" + object2.attributes['alignment']
            else:
                rule['alignment'] = 'NA'

            if ('shape' in object1.attributes) and ('shape' in object2.attributes):
                if object1.attributes['shape'] == object2.attributes['shape']:
                    rule['shape'] = 'identical'
                else:
                    rule['shape'] = 'changed'
            else:
                rule['shape'] = 'NA'

            if ('fill' in object1.attributes) and ('fill' in object2.attributes):
                if object1.attributes['fill'] == object2.attributes['fill']:
                    rule['fill'] = 'identical'
                else:
                    rule['fill'] = 'changed'
            else:
                rule['fill'] = 'NA'

            if ('above' in object1.attributes) and ('above' in object2.attributes):
                rule['above'] = 'above'
            else:
                rule['above'] = 'NA'

            if ('overlaps' in object1.attributes) and ('overlaps' in object2.attributes):
                rule['overlaps'] = 'overlaps'
            else:
                rule['overlaps'] = 'NA'

            if ('inside' in object1.attributes) and ('inside' not in object2.attributes):
                rule['inside'] = 'removed'
            elif ('inside' not in object1.attributes) and ('inside' in object2.attributes):
                rule['inside'] = 'added'
            elif 'inside' in object1.attributes and 'inside' in object2.attributes:
                rule['inside'] = 'identical'
            else:
                rule['inside'] = 'NA'

            return(rule)

        ##############################
        ##
        ## Computing alignment score
        ##
        ##############################

        def compute_alignment_score(transformation1, transformation2, transformation3, transformation4):

            '''
            transformation1: A -> B
            transformation2: C -> D
            transformation3: A -> C
            transformation4: B -> D
            '''

            alignments_A_B = transformation1.split("_")
            alignments_C_D = transformation2.split("_")

            alignmentA = alignments_A_B[0]
            alignmentB = alignments_A_B[1]
            alignmentC = alignments_C_D[0]
            alignmentD = alignments_C_D[1]

            ###########################
            ##
            ## Hash method
            ##
            ###########################

            alignments_hash = {"top-left":0, "top-right":1, "bottom-left":2, "bottom-right":3}

            alignment_AB_diff = alignments_hash[alignmentA] - alignments_hash[alignmentB]
            alignment_CD_diff = alignments_hash[alignmentC] - alignments_hash[alignmentD]
            alignment_AC_diff = alignments_hash[alignmentA] - alignments_hash[alignmentC]
            alignment_BD_diff = alignments_hash[alignmentB] - alignments_hash[alignmentD]

            if (alignment_AB_diff == alignment_CD_diff) and (alignment_AC_diff == alignment_BD_diff):
                return True
            else:
                return False          

        ##############################
        ##
        ## Computing angle change
        ##
        ##############################

        def compute_angle_score(transformation1, transformation2, transformation3, transformation4):

            '''
            transformation1: A -> B
            transformation2: C -> D
            transformation3: A -> C
            transformation4: B -> D
            '''

            if (transformation1 == transformation2) and (transformation3 == transformation4):
                return True

            if transformation1 == 'identical' and transformation2 != 'identical':
                return False

            if transformation2 == 'identical' and transformation1 != 'identical':
                return False

            if transformation3 == 'identical' and transformation4 != 'identical':
                return False

            if transformation4 == 'identical' and transformation3 != 'identical':
                return False

            # Computing angle change
            
            angles_a_b = transformation1.split("_")
            angle_a = int(float(angles_a_b[0]))
            angle_b = int(float(angles_a_b[1]))

            angles_c_d = transformation2.split("_")
            angle_c = int(float(angles_c_d[0]))
            angle_d = int(float(angles_c_d[1]))

            x_symmetry = False
            y_symmetry = False

            # X-axis

            if ((angle_a + angle_c) == 360) and ((angle_b + angle_d) == 360):
                x_symmetry = True

            # Y-axis

            if ((angle_a + angle_b == 180) or (angle_a + angle_b == 540)) and ((angle_c + angle_d == 180) or (angle_c + angle_d == 540)):
                y_symmetry = True

            return x_symmetry and y_symmetry

        ##############################
        ##
        ## Same object solution
        ##
        ##############################

        def scoring_function(transformation1, transformation2, transformation3, transformation4):

            '''
            transformation1: A -> B
            transformation2: C -> D
            transformation3: A -> C
            transformation4: B -> D
            '''

            transformation1_length = len(transformation1)
            transformation2_length = len(transformation2)
            transformation3_length = len(transformation3)
            transformation4_length = len(transformation4)
            final_score = 0

            for i in range(transformation1_length):

                rule_A_B = transformation1[i]
                rule_C_D = transformation2[i]
                rule_A_C = transformation3[i]
                rule_B_D = transformation4[i]

                # shape: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['shape'] != 'NA' and rule_C_D['shape'] != 'NA':
                    if rule_A_B['shape'] == rule_C_D['shape']:
                        final_score += 1

                if rule_A_C['shape'] != 'NA' and rule_B_D['shape'] != 'NA':
                    if rule_A_C['shape'] == rule_B_D['shape']:
                        final_score += 1

                # fill: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['fill'] != 'NA' and rule_C_D['fill'] != 'NA':
                    if rule_A_B['fill'] == rule_C_D['fill']:
                        final_score += 1

                if rule_A_C['fill'] != 'NA' and rule_B_D['fill'] != 'NA':
                    if rule_A_C['fill'] == rule_B_D['fill']:
                        final_score += 1

                # size: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['size'] != 'NA' and rule_C_D['size'] != 'NA':
                    if rule_A_B['size'] == rule_C_D['size']:
                        final_score += 1

                if rule_A_C['size'] != 'NA' and rule_B_D['size'] != 'NA':
                    if rule_A_C['size'] == rule_B_D['size']:
                        final_score += 1

                # inside: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['inside'] != 'NA' and rule_C_D['inside'] != 'NA':
                    if rule_A_B['inside'] == rule_C_D['inside']:
                        final_score += 1

                if rule_A_C['inside'] != 'NA' and rule_B_D['inside'] != 'NA':
                    if rule_A_C['inside'] == rule_B_D['inside']:
                        final_score += 1

                # above: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['above'] != 'NA' and rule_C_D['above'] != 'NA':
                    if rule_A_B['above'] == rule_C_D['above']:
                        final_score += 1

                if rule_A_C['above'] != 'NA' and rule_B_D['above'] != 'NA':
                    if rule_A_C['above'] == rule_B_D['above']:
                        final_score += 1

                # overlap: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['overlaps'] != 'NA' and rule_C_D['overlaps'] != 'NA':
                    if rule_A_B['overlaps'] == rule_C_D['overlaps']:
                        final_score += 1

                if rule_A_C['overlaps'] != 'NA' and rule_B_D['overlaps'] != 'NA':
                    if rule_A_C['overlaps'] == rule_B_D['overlaps']:
                        final_score += 1

                # angle: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if (rule_A_B['angle'] != 'NA') and (rule_C_D['angle'] != 'NA') and (rule_A_C['angle'] != 'NA') and (rule_B_D['angle'] != 'NA'):

                    angle_pattern = compute_angle_score(rule_A_B['angle'], rule_C_D['angle'], rule_A_C['angle'], rule_B_D['angle'])

                    if angle_pattern:
                        final_score += 2

                # angle: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if (rule_A_B['alignment'] != 'NA') and (rule_C_D['alignment'] != 'NA') and (rule_A_C['alignment'] != 'NA') and (rule_B_D['alignment'] != 'NA'):

                    alignment_pattern = compute_alignment_score(rule_A_B['alignment'], rule_C_D['alignment'], rule_A_C['alignment'], rule_B_D['alignment'])

                    if alignment_pattern:
                        final_score += 2

            return final_score

        ##############################
        ##
        ## remove object solution
        ##
        ##############################

        def scoring_function_remove(transformation1, transformation2, transformation3, transformation4):

            '''
            transformation1: A -> B
            transformation2: C -> D
            transformation3: A -> C
            transformation4: B -> D
            '''

            transformation1_length = len(transformation1)
            transformation2_length = len(transformation2)
            transformation3_length = len(transformation3)
            transformation4_length = len(transformation4)
            final_score = 0

            print "removed: "
            print "a to b: ", transformation1_length
            print "c to d: ", transformation2_length
            print "a to c: ", transformation3_length
            print "b to d: ", transformation4_length

            for i in range(transformation1_length):

                rule_A_B = transformation1[i]
                rule_C_D = transformation2[i]
                rule_A_C = transformation3[i]
                rule_B_D = transformation4[0]

                # shape: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['shape'] != 'NA' and rule_C_D['shape'] != 'NA':
                    if rule_A_B['shape'] == rule_C_D['shape']:
                        final_score += 1

                if rule_A_C['shape'] != 'NA' and rule_B_D['shape'] != 'NA':
                    if rule_A_C['shape'] == rule_B_D['shape']:
                        final_score += 1

                # fill: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['fill'] != 'NA' and rule_C_D['fill'] != 'NA':
                    if rule_A_B['fill'] == rule_C_D['fill']:
                        final_score += 1

                if rule_A_C['fill'] != 'NA' and rule_B_D['fill'] != 'NA':
                    if rule_A_C['fill'] == rule_B_D['fill']:
                        final_score += 1

                # size: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['size'] != 'NA' and rule_C_D['size'] != 'NA':
                    if rule_A_B['size'] == rule_C_D['size']:
                        final_score += 1

                if rule_A_C['size'] != 'NA' and rule_B_D['size'] != 'NA':
                    if rule_A_C['size'] == rule_B_D['size']:
                        final_score += 1

                # inside: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['inside'] != 'NA' and rule_C_D['inside'] != 'NA':
                    if rule_A_B['inside'] == rule_C_D['inside']:
                        final_score += 1

                if rule_A_C['inside'] != 'NA' and rule_B_D['inside'] != 'NA':
                    if rule_A_C['inside'] == rule_B_D['inside']:
                        final_score += 1

                # above: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['above'] != 'NA' and rule_C_D['above'] != 'NA':
                    if rule_A_B['above'] == rule_C_D['above']:
                        final_score += 1

                if rule_A_C['above'] != 'NA' and rule_B_D['above'] != 'NA':
                    if rule_A_C['above'] == rule_B_D['above']:
                        final_score += 1

                # overlap: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['overlaps'] != 'NA' and rule_C_D['overlaps'] != 'NA':
                    if rule_A_B['overlaps'] == rule_C_D['overlaps']:
                        final_score += 1

                if rule_A_C['overlaps'] != 'NA' and rule_B_D['overlaps'] != 'NA':
                    if rule_A_C['overlaps'] == rule_B_D['overlaps']:
                        final_score += 1

                # angle: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if (rule_A_B['angle'] != 'NA') and (rule_C_D['angle'] != 'NA') and (rule_A_C['angle'] != 'NA') and (rule_B_D['angle'] != 'NA'):

                    angle_pattern = compute_angle_score(rule_A_B['angle'], rule_C_D['angle'], rule_A_C['angle'], rule_B_D['angle'])

                    if angle_pattern:
                        final_score += 2

                # angle: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if (rule_A_B['alignment'] != 'NA') and (rule_C_D['alignment'] != 'NA') and (rule_A_C['alignment'] != 'NA') and (rule_B_D['alignment'] != 'NA'):

                    alignment_pattern = compute_alignment_score(rule_A_B['alignment'], rule_C_D['alignment'], rule_A_C['alignment'], rule_B_D['alignment'])

                    if alignment_pattern:
                        final_score += 2

            return final_score

        ##############################
        ##
        ## add object solution
        ##
        ##############################

        def scoring_function_add(transformation1, transformation2, transformation3, transformation4):

            '''
            transformation1: A -> B
            transformation2: C -> D
            transformation3: A -> C
            transformation4: B -> D
            '''

            transformation1_length = len(transformation1)
            transformation2_length = len(transformation2)
            transformation3_length = len(transformation3)
            transformation4_length = len(transformation4)
            final_score = 0

            print "Added: "
            print "a to b: ", transformation1_length
            print "c to d: ", transformation2_length
            print "a to c: ", transformation3_length
            print "b to d: ", transformation4_length


            for i in range(transformation1_length):

                rule_A_B = transformation1[i]
                rule_C_D = transformation2[i]
                rule_A_C = transformation3[0]
                rule_B_D = transformation4[i]

                # shape: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['shape'] != 'NA' and rule_C_D['shape'] != 'NA':
                    if rule_A_B['shape'] == rule_C_D['shape']:
                        final_score += 1

                if rule_A_C['shape'] != 'NA' and rule_B_D['shape'] != 'NA':
                    if rule_A_C['shape'] == rule_B_D['shape']:
                        final_score += 1

                # fill: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['fill'] != 'NA' and rule_C_D['fill'] != 'NA':
                    if rule_A_B['fill'] == rule_C_D['fill']:
                        final_score += 1

                if rule_A_C['fill'] != 'NA' and rule_B_D['fill'] != 'NA':
                    if rule_A_C['fill'] == rule_B_D['fill']:
                        final_score += 1

                # size: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['size'] != 'NA' and rule_C_D['size'] != 'NA':
                    if rule_A_B['size'] == rule_C_D['size']:
                        final_score += 1

                if rule_A_C['size'] != 'NA' and rule_B_D['size'] != 'NA':
                    if rule_A_C['size'] == rule_B_D['size']:
                        final_score += 1

                # inside: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['inside'] != 'NA' and rule_C_D['inside'] != 'NA':
                    if rule_A_B['inside'] == rule_C_D['inside']:
                        final_score += 1

                if rule_A_C['inside'] != 'NA' and rule_B_D['inside'] != 'NA':
                    if rule_A_C['inside'] == rule_B_D['inside']:
                        final_score += 1

                # above: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['above'] != 'NA' and rule_C_D['above'] != 'NA':
                    if rule_A_B['above'] == rule_C_D['above']:
                        final_score += 1

                if rule_A_C['above'] != 'NA' and rule_B_D['above'] != 'NA':
                    if rule_A_C['above'] == rule_B_D['above']:
                        final_score += 1

                # overlap: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if rule_A_B['overlaps'] != 'NA' and rule_C_D['overlaps'] != 'NA':
                    if rule_A_B['overlaps'] == rule_C_D['overlaps']:
                        final_score += 1

                if rule_A_C['overlaps'] != 'NA' and rule_B_D['overlaps'] != 'NA':
                    if rule_A_C['overlaps'] == rule_B_D['overlaps']:
                        final_score += 1

                # angle: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if (rule_A_B['angle'] != 'NA') and (rule_C_D['angle'] != 'NA') and (rule_A_C['angle'] != 'NA') and (rule_B_D['angle'] != 'NA'):

                    angle_pattern = compute_angle_score(rule_A_B['angle'], rule_C_D['angle'], rule_A_C['angle'], rule_B_D['angle'])

                    if angle_pattern:
                        final_score += 2

                # angle: attribute_list = ['shape', 'fill', 'size', 'angle', 'inside', 'above', 'overlaps', 'alignment']

                if (rule_A_B['alignment'] != 'NA') and (rule_C_D['alignment'] != 'NA') and (rule_A_C['alignment'] != 'NA') and (rule_B_D['alignment'] != 'NA'):

                    alignment_pattern = compute_alignment_score(rule_A_B['alignment'], rule_C_D['alignment'], rule_A_C['alignment'], rule_B_D['alignment'])

                    if alignment_pattern:
                        final_score += 2

            return final_score


        ##############################
        ##
        ## Generate solutions for 2x2
        ##
        ##############################

        def solve2x2(figure_A, figure_B, figure_C):

            figure_A_object_keys = sorted(figure_A.objects.keys())
            figure_B_object_keys = sorted(figure_B.objects.keys())
            figure_C_object_keys = sorted(figure_C.objects.keys())

            num_figure_A_object_keys = len(figure_A_object_keys)
            num_figure_B_object_keys = len(figure_B_object_keys)
            num_figure_C_object_keys = len(figure_C_object_keys)

            A_B_transformations = []
            #C_D_transformations = []
            A_C_transformations = []
            #B_D_transformations = []
            score_hash = {}
            print "Problem: ", problem.name
            print "Candidates: ", candidates, "\n\n"

            ###########
            ##
            ## 1 Object
            ##
            ###########

            if (num_figure_A_object_keys == 1) and (num_figure_B_object_keys == 1) and (num_figure_C_object_keys == 1):

                for j in range(num_figure_A_object_keys):

                    key_A = figure_A_object_keys[j]
                    key_B = figure_B_object_keys[j]
                    key_C = figure_C_object_keys[j]

                    A_to_B = generate_transformation_rules(figure_A.objects[key_A], figure_B.objects[key_B])
                    A_to_C = generate_transformation_rules(figure_A.objects[key_A], figure_C.objects[key_C])

                    A_B_transformations.append(A_to_B)
                    A_C_transformations.append(A_to_C)

                for candidate_key in candidates:

                    C_D_transformations = []
                    B_D_transformations = []

                    for k in range(num_figure_B_object_keys):
                    
                        key_B = figure_B_object_keys[k]
                        key_C = figure_C_object_keys[k]

                        figure_D = problem.figures[candidate_key]
                        figure_D_object_keys = sorted(figure_D.objects.keys())
                        key_D = figure_D_object_keys[k]

                        C_to_D = generate_transformation_rules(figure_C.objects[key_C], figure_D.objects[key_D])
                        B_to_D = generate_transformation_rules(figure_B.objects[key_B], figure_D.objects[key_D])

                        C_D_transformations.append(C_to_D)
                        B_D_transformations.append(B_to_D)

                    candidate_score = scoring_function(A_B_transformations, C_D_transformations, A_C_transformations, B_D_transformations)

                    score_hash[candidate_key] = candidate_score

                sorted_candidates = sorted(score_hash, key=(lambda key:score_hash[key]), reverse=True)
                final_candidate = sorted_candidates[0]

                print "Problem: ", problem.name
                print "Candidate 1: ", final_candidate, " -> ", score_hash[final_candidate]
                print "Candidate 2: ", sorted_candidates[1], " -> ", score_hash[sorted_candidates[1]]

                return int(final_candidate)

            ###########
            ##
            ## 1 Object removed from A
            ##
            ###########

            if (num_figure_A_object_keys == 2) and (num_figure_B_object_keys == 1) and (num_figure_C_object_keys == 2):

                for j in range(num_figure_A_object_keys):

                    key_A = figure_A_object_keys[j]
                    key_B = figure_B_object_keys[0]
                    key_C = figure_C_object_keys[j]

                    A_to_B = generate_transformation_rules(figure_A.objects[key_A], figure_B.objects[key_B])
                    A_to_C = generate_transformation_rules(figure_A.objects[key_A], figure_C.objects[key_C])

                    A_B_transformations.append(A_to_B)
                    A_C_transformations.append(A_to_C)

                for candidate_key in candidates:

                    C_D_transformations = []
                    B_D_transformations = []

                    key_B = figure_B_object_keys[0]
                    figure_D = problem.figures[candidate_key]
                    figure_D_object_keys = sorted(figure_D.objects.keys())
                    key_D = figure_D_object_keys[0]
                    B_to_D = generate_transformation_rules(figure_B.objects[key_B], figure_D.objects[key_D])
                    B_D_transformations.append(B_to_D)

                    for k in range(num_figure_C_object_keys):
                    
                        key_C = figure_C_object_keys[k]
                        C_to_D = generate_transformation_rules(figure_C.objects[key_C], figure_D.objects[key_D])
                        C_D_transformations.append(C_to_D)
                    
                    candidate_score = scoring_function_remove(A_B_transformations, C_D_transformations, A_C_transformations, B_D_transformations)

                    score_hash[candidate_key] = candidate_score

                sorted_candidates = sorted(score_hash, key=(lambda key:score_hash[key]), reverse=True)
                final_candidate = sorted_candidates[0]

                print "Problem: ", problem.name
                print "Candidate 1: ", final_candidate, " -> ", score_hash[final_candidate]
                print "Candidate 2: ", sorted_candidates[1], " -> ", score_hash[sorted_candidates[1]]

                return int(final_candidate)

            ###########
            ##
            ## 1 Object added to A
            ##
            ###########

            if (num_figure_A_object_keys == 1) and (num_figure_B_object_keys == 2) and (num_figure_C_object_keys == 1):

                key_A = figure_A_object_keys[0]
                key_C = figure_C_object_keys[0]
                A_to_C = generate_transformation_rules(figure_A.objects[key_A], figure_C.objects[key_C])
                A_C_transformations.append(A_to_C)


                for j in range(num_figure_B_object_keys):
                
                    key_B = figure_B_object_keys[j]
                    A_to_B = generate_transformation_rules(figure_A.objects[key_A], figure_B.objects[key_B])
                    A_B_transformations.append(A_to_B)
                

                for candidate_key in candidates:

                    C_D_transformations = []
                    B_D_transformations = []

                    for k in range(num_figure_B_object_keys):
                    
                        key_B = figure_B_object_keys[k]
                        key_C = figure_C_object_keys[0]

                        figure_D = problem.figures[candidate_key]
                        figure_D_object_keys = sorted(figure_D.objects.keys())
                        key_D = figure_D_object_keys[k]

                        C_to_D = generate_transformation_rules(figure_C.objects[key_C], figure_D.objects[key_D])
                        B_to_D = generate_transformation_rules(figure_B.objects[key_B], figure_D.objects[key_D])
                        C_D_transformations.append(C_to_D)
                        B_D_transformations.append(B_to_D)

                    candidate_score = scoring_function_add(A_B_transformations, C_D_transformations, A_C_transformations, B_D_transformations)

                    score_hash[candidate_key] = candidate_score

                sorted_candidates = sorted(score_hash, key=(lambda key:score_hash[key]), reverse=True)
                final_candidate = sorted_candidates[0]

                print "Problem: ", problem.name
                print "Candidate 1: ", final_candidate, " -> ", score_hash[final_candidate]
                print "Candidate 2: ", sorted_candidates[1], " -> ", score_hash[sorted_candidates[1]]

                return int(final_candidate)

            ###########
            ##
            ## 2 Objects
            ##
            ###########

            if (num_figure_A_object_keys == 2) and (num_figure_B_object_keys == 2) and (num_figure_C_object_keys == 2):

                for j in range(num_figure_A_object_keys):

                    key_A = figure_A_object_keys[j]
                    key_B = figure_B_object_keys[j]
                    key_C = figure_C_object_keys[j]

                    A_to_B = generate_transformation_rules(figure_A.objects[key_A], figure_B.objects[key_B])
                    A_to_C = generate_transformation_rules(figure_A.objects[key_A], figure_C.objects[key_C])

                    A_B_transformations.append(A_to_B)
                    A_C_transformations.append(A_to_C)

                for candidate_key in candidates:

                    C_D_transformations = []
                    B_D_transformations = []

                    for k in range(num_figure_B_object_keys):
                    
                        key_B = figure_B_object_keys[k]
                        key_C = figure_C_object_keys[k]

                        figure_D = problem.figures[candidate_key]
                        figure_D_object_keys = sorted(figure_D.objects.keys())
                        key_D = figure_D_object_keys[k]

                        C_to_D = generate_transformation_rules(figure_C.objects[key_C], figure_D.objects[key_D])
                        B_to_D = generate_transformation_rules(figure_B.objects[key_B], figure_D.objects[key_D])

                        C_D_transformations.append(C_to_D)
                        B_D_transformations.append(B_to_D)

                    candidate_score = scoring_function(A_B_transformations, C_D_transformations, A_C_transformations, B_D_transformations)

                    score_hash[candidate_key] = candidate_score

                sorted_candidates = sorted(score_hash, key=(lambda key:score_hash[key]), reverse=True)
                final_candidate = sorted_candidates[0]

                print "Problem: ", problem.name
                print "Candidate 1: ", final_candidate, " -> ", score_hash[final_candidate]
                print "Candidate 2: ", sorted_candidates[1], " -> ", score_hash[sorted_candidates[1]]

                return int(final_candidate)


            elif num_figure_A_object_keys > num_figure_B_object_keys:

                return np.max([int(x) for x in candidates])

            elif num_figure_A_object_keys < num_figure_B_object_keys:

                return np.max([int(x) for x in candidates])

            elif num_figure_A_object_keys > num_figure_C_object_keys:

                return np.max([int(x) for x in candidates])

            elif num_figure_A_object_keys < num_figure_C_object_keys:

                return np.max([int(x) for x in candidates])

            else:

                return -1

        #################################
        ###
        ### Load 3x3 figures
        ###
        #################################

        def load_3x3_image(problem, key):
            
            filename = problem.figures[key].visualFilename
            return Image.open(os.path.join(sys.path[0], filename))

        #################################
        ###
        ### Normalize Pillow images
        ###
        #################################

        def image_normalization(image_list):

            normalized_image_list = image_list

            for i in range(len(image_list)):
                image = image_list[i]
                image = image.resize((184,184))
                gray_scale = image.convert('L')
                gray_array = np.asarray(gray_scale).copy()
                gray_array[gray_array < 70] = 0
                gray_array[gray_array >= 70] = 255
                normalized_image = Image.fromarray(gray_array)
                normalized_image_list[i] = normalized_image

            return normalized_image_list

        #################################
        ###
        ### Compute Pixels Percentage
        ###
        #################################

        def pixels_percentage(image):
            pixels = image.size[0] * image.size[1]
            return (np.count_nonzero(image) / pixels) * 100


        #################################
        ###
        ### ADD rule judgement
        ###
        #################################

        def AND_rule_judgement(image1, image2, image3):

            image1_2 = Chops.add(image1, image2)


        #################################
        ###
        ### Using ADD rule
        ###
        #################################

        def apply_AND_rule(normalized_question_figure_list, normalized_anwser_figure_list):

            [figure_A, figure_B, figure_C, figure_D, figure_E, figure_F, figure_G, figure_H] = normalized_question_figure_list

            A_AND_B_AND_C = AND_rule_judgement(figure_A, figure_B, figure_C)
            D_AND_E_AND_F = AND_rule_judgement(figure_D, figure_E, figure_F)

        # If first and second row exhibit OR pattern, see if we can find an accurate third-row solution
        if self.exhibits_AND(im_a, im_b, im_c) and self.exhibits_AND(im_d, im_e, im_f):
            for i, answer in enumerate(answers):
                if self.exhibits_AND(im_g, im_h, answer):
                    return i+1

        return -1



        #################################
        ###
        ### Solve 2x2 
        ###
        #################################

        if problem.problemType == "2x2":

            ##############################
            ##
            ## Reading Figure A, B, C
            ##
            ##############################

            figure_A = problem.figures['A']
            figure_B = problem.figures['B']
            figure_C = problem.figures['C']
            figures_diff = len(figure_A.objects) - len(figure_B.objects)

            ##############################
            ##
            ## Filtered out the wrong anwsers that A.objects - B.objects != C.objects - D.objects
            ##
            ##############################

            candidates = []

            for figure_key in problem.figures:
                if figure_key not in ['A', 'B', 'C']:
                    actual_diff = len(figure_C.objects) - len(problem.figures[figure_key].objects)

                    if actual_diff == figures_diff:
                        candidates.append(figure_key)

            # Only one candidates

            if len(candidates) == 1:
                return int(candidates[0])
            else:
                return solve2x2(figure_A, figure_B, figure_C)

        #################################
        ###
        ### Solve 3x3 
        ###
        #################################

        elif problem.problemType == "3x3":

            print "3x3 Problem: ", problem.name
            
            try:
                figure_A = load_3x3_image(problem, 'A')
                figure_B = load_3x3_image(problem, 'B')
                figure_C = load_3x3_image(problem, 'C')
                figure_D = load_3x3_image(problem, 'D')
                figure_E = load_3x3_image(problem, 'E')
                figure_F = load_3x3_image(problem, 'F')
                figure_G = load_3x3_image(problem, 'G')
                figure_H = load_3x3_image(problem, 'H')
            except IOError as e:
                print('Could not open the QUESTION image: IO issue')
                print(e)

            try:
                figure_1 = load_3x3_image(problem, '1')
                figure_2 = load_3x3_image(problem, '2')
                figure_3 = load_3x3_image(problem, '3')
                figure_4 = load_3x3_image(problem, '4')
                figure_5 = load_3x3_image(problem, '5')
                figure_6 = load_3x3_image(problem, '6')
                figure_7 = load_3x3_image(problem, '7')
                figure_8 = load_3x3_image(problem, '8')
            except IOError as e:
                print('Could not open the ANWSWER image: IO issue')
                print(e)


            question_figure_list = [figure_A, figure_B, figure_C, figure_D, figure_E, figure_F, figure_G, figure_H]
            anwser_figure_list   = [figure_1, figure_2, figure_3, figure_4, figure_5, figure_6, figure_7, figure_8]

            normalized_question_figure_list = image_normalization(question_figure_list)
            normalized_anwser_figure_list   = image_normalization(anwser_figure_list)

            #print normalized_question_figure_list
            #print normalized_anwser_figure_list

            #print(figure_A.format, figure_A.size, figure_A.mode)
            #print(figure_1.format, figure_1.size, figure_1.mode)

            ##############################
            ##
            ## Using AND rule
            ##
            ##############################

            AND_rule_anwswer = apply_AND_rule(normalized_question_figure_list, normalized_anwser_figure_list)

            if AND_rule_anwswer > -1:
                print ("Problem is solved by ADD rule.")
                return AND_rule_anwswer


            return -1

        else:

            return -1

