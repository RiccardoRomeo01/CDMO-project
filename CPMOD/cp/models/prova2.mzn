include "globals.mzn";
include "alldifferent.mzn";

int: m; %number of couriers
set of int: COURIER= 1..m;
array[COURIER] of int: l;%the maximum load for couriers

int: n;%number of item
set of int: ITEM=1..n;
array[ITEM] of int: s;%the size of the item

array [1..n+1,1..n+1] of int: D;

int: up_bound;
int :low_bound;
int :d_low_bound;


array[ITEM] of var COURIER: assigned;






int: max_num_of_item=min([ceil(n/m)+2,n]);
array[COURIER] of var 1..max_num_of_item: num_of_item;
array[COURIER,1..max_num_of_item+2] of var 1..n+1: pos;
%to change

constraint forall(c in COURIER)(pos[c,1]=n+1);
constraint forall(c in COURIER)(pos[c,max_num_of_item+2]=n+1);


array[COURIER] of var d_low_bound..up_bound: obj_dist;

var d_low_bound..up_bound: makespan; %I can use low_bound to stop the algoritm in the correct solution



% ensure that each courier does not exceed the max capacity
constraint bin_packing_capa(l,assigned,s);
  
       
                                                  
                                                                                                  
constraint forall(k in COURIER) (
      obj_dist[k] = sum([D[pos[k,i],pos[k,i+1] ]| i in 1..max_num_of_item+1] )
  );

   
constraint forall(c in COURIER) ( 
  count_eq(assigned, c, num_of_item[c])%con questo si calcola il numero di item per ogni courier
);
constraint forall(c in COURIER)(
  forall(i in 2..max_num_of_item+2 ) (
  if i<=num_of_item[c]+1 then
  assigned[pos[c,i]]=c /\
  pos[c,i]!=n+1 else
  pos[c,i]=n+1 endif
  ));
  


constraint alldifferent_except(pos,{n+1});


constraint makespan = max(obj_dist);
 
  



  
  
  
 


solve :: seq_search([
                int_search(pos, first_fail, indomain_min),
                int_search(assigned, first_fail, indomain_min),
                
                ])
     minimize(makespan);



