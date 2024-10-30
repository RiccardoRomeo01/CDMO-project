/*
 * Description of the model :
 * we use a 2D array to handle the assignment of object to each m. 
 * The matrix dimension is Courier x Item + 1, each m has an associated
 * array where for each element of the array can be assigned a value from 1 to n + 1.
 * This means that each m goes from i (position of array) to j (value assigned to cell).
 */
include "alldifferent.mzn";
include "globals.mzn";


% Input variables
int: m;
int: n;
int: up_bound;
int :low_bound;
int :d_low_bound;

% useful sets
set of int: COURIER = 1..m;
set of int: ITEMS = 1..n;
set of int: NODES = 1..n + 1;

array[COURIER] of int: l;
array[ITEMS] of int: s;
array[NODES, NODES] of int: D; 

% Model variables
array[COURIER] of var d_low_bound..up_bound: obj_dist;
array[COURIER, NODES] of var NODES: pos;

% objective function


var low_bound..up_bound: maximum; 

int :max_load = max(l) + 1;

array[ITEMS] of var 0..m: assigned;

array[COURIER] of var 0..max_load: ms_assigned;


% ensure that each m starts and ends in origin point
constraint forall(k in COURIER) (
      if pos[k, n+1] != n+1 then count([pos[k, i] | i in ITEMS], n+1, 1) 
      else forall(i in NODES) (pos[k, i] == i)  endif
);

% each item must be assigned only to one m
constraint forall(i in ITEMS)(
      count([pos[k, i]| k in COURIER], i, m-1)
);


% setting the assigned to verify the load_size for each m
constraint forall(k in COURIER) (
          forall(i in ITEMS)(
          if pos[k, i] != i then
          assigned[i] = k endif
           )
);

% ensure that each m does not exceed the max capacity
constraint bin_packing_capa(
                           l,
                           assigned,
                           s);

% Circuit
constraint forall(k in COURIER) (
      subcircuit([pos[k, i] |i in NODES]) 
);

% distance computation
constraint forall(k in COURIER) (
      obj_dist[k] = sum([D[i, pos[k, i]]| i in NODES where pos[k, i] != i])
);


% Symmetry breaking constraint
constraint forall(k in COURIER)(
    ms_assigned[k] = sum(
            [s[i] | i in ITEMS where assigned[i]=k]
    )
);

% sub tour elimination, if the last m can carry all the packages
% then all m must start
constraint forall(k in COURIER) (
                  if l[m] >= max(s) then 
                  pos[k, n+1] != n+1   
                  endif
            );

/*
This is equal to the previous symmetry, it is another way to rewrite it
% Symmetry breaking 
constraint forall(k in 1..m-1) (
      ms_assigned[k] >= ms_assigned[k+1]
);
*/
constraint maximum = max(obj_dist);
 


solve :: seq_search([
                int_search(pos, first_fail, indomain_min),
                int_search(assigned, first_fail, indomain_min)])
     minimize(maximum);

%solve minimize(max(obj_dist));

%output [show(obj_dist) ++ "\n"];

%output [show(symmetry[i, 1]) ++ " "| i in NODES]