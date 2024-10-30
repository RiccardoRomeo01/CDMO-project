include "globals.mzn";
include "alldifferent.mzn";

int: m; %number of couriers
set of int: COURIER= 1..m;
array[COURIER] of int: l;%the maximum load for couriers

int: n;%number of item
set of int: ITEM=1..n;
array[ITEM] of int: s;%the size of the item


array [1..n+1,1..n+1] of int: D;

array[ITEM] of var COURIER: assigned;
array[COURIER] of var int: num_of_item;

array[COURIER,1..n+2] of var int: pos;
constraint forall(c in COURIER)(pos[c,1]=n+1);
constraint forall(c in COURIER)(pos[c,n+2]=n+1);

var 0..1000: makespan; %to change 1000

constraint forall(c in COURIER) ( 
  count_eq(assigned, c, num_of_item[c])%con questo si calcola il numero di item per ogni courier
);

constraint forall(c in COURIER)(
  sum([s[i]| i in ITEM where assigned[i]=c])<=l[c]
);

constraint forall(c in COURIER)( among(num_of_item[c],pos[c,1..n+2],ITEM)  );%contraint that all the item are delivered

constraint forall(c in COURIER)(
  forall(i in 1..n) (among(1,pos[c,1..n+2],i..i) \/ assigned[i]!=c
  ) );%all the courier delivered only the item assigned

constraint alldifferent_except(pos,{n+1});


constraint
    forall(c in COURIER)(
        sum([D[pos[c,i],pos[c,i+1] ]| i in 1..n+1] ) <=makespan
  );
  
  
  
  
  
  
  
array[COURIER,1..n+1] of var int: dis;
array[COURIER] of var int: totDis;
constraint forall(c in COURIER)(
    forall(i in 1..n+1)(
        dis[c,i]=D[pos[c,i],pos[c,i+1]]
  ) /\
  totDis[c]=sum([D[pos[c,i],pos[c,i+1] ]| i in 1..n+1] )
  );

solve :: seq_search([
                int_search(pos, first_fail, indomain_min),
                int_search(assigned, first_fail, indomain_min)])
     minimize(makespan);

output [
    "assigned = ", show(assigned), "\n",
    "num_of_item = ", show(num_of_item), "\n",
    "pos = ", show(pos), "\n",
    "dis  ",show(dis),"\n",
    "totdis  ",show(totDis),"\n",
    
    
    
    
];

