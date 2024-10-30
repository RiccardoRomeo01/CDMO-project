from CPMOD.cp.utils import *

def print_model(evaluated_results, corresponding_dict):
    (asg,
     obj_dist,
     distances,
     seconds) = evaluated_results
    
    '''
    for k in range(len(asg)):
        print("Courier = ", corresponding_dict[k])
        for i in range(len(asg[k])-1):
            if asg[k][i] != i + 1:
                print("Starting Node: {} Ending Node: {} ({} km)".format(
                                                                i + 1, 
                                                                asg[corresponding_dict[k]][i],
                                                                distances[i][asg[corresponding_dict[k]][i] - 1]
                                                                )
                )
                '''
    print("Total distances = ", obj_dist)
    print("TIME =", seconds)
    print("---------------------------------------------")


def sorting_correspondence(res, corresponding_dict):
    '''
    Takes the output of the model and change the positions
    according to the corresponding dictionary.

    Final res will contain the list with output where all the result
    are provided according to the original order, before the sorting of
    couriers

    '''
    final_res = [[] for _ in range(len(res))]
    if len(res) != len(corresponding_dict):
        return res

    # Assigned the corrispondences with the dictionary
    for i in range(len(res)):
        courier = corresponding_dict[i]
        final_res[courier] = res[i]
    return final_res



def format_output_cp_model(evaluated_result, optimal, corresponding_dict):
    '''
    Create the the dictionary to save in the output folder, it needs to
    convert the assignment format in a list containing only the correct
    assignments.
    '''
    (assignments,
     obj_dist,
     distances,
     seconds
    )=evaluated_result



    seconds = seconds.__floor__()
    obj = max(obj_dist)

    items = len(assignments[0])
    
    res = []
    
    for k in range(len(assignments)):
        temp=assignments[k]
        t=[]
        m=max(temp)
        for i in temp:
            if(i!=m):
                t.append(i)
        
        res.append(t)
        #print(t)
    final_res = sorting_correspondence(res,corresponding_dict)

    return get_dict(seconds, optimal, obj, final_res)