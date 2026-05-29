#### sampling_design_generation.R

#Generating experimental designs for SJV spatial optimization (SJVSO) batching
#and sensitivity/robustness analysis

#This script generates csv file outputs where each row
#represents a particular parameter combination of inputs that can be run
#through SJVSO in batch mode to explore the behavior.

#full-factorial: Specify levels of each variable, and every combination of 
#every variable is generated. Good for exploring interactions to test whether 
#the effect of changing one variable is different depending on the values 
#the other variables are at.

#latin hypercube: a "space-filling" design that "smartly" chooses points to 
#sample within the range of inputs. Has some randomness. (But you can set the 
#seed to avoid that)

library(lhs)

# Templates and output live in this directory. Defaults to `data/` so the
# script can be run from the repository root without edits.
exp_dir <- "data"
design_info_file <- file.path(exp_dir, "exp_design_FF_LHS_template_prep_shot_20251024.csv")
export_name <- "experimental_design.csv"
n_points <- 1000


################################################################################
####
####  Preliminaries - specifying variables, experimental designs, etc.
####
################################################################################

#Write directory: Where do you want your experimental design csv's to go?
# exp_dir <- "C:/Research_NUS/SJV_Spatial_RDM/code/inputs_hand-curated"


#Read in and perform checks for relevant info:
design_info <- read.csv(design_info_file)
stopifnot(c("variables", "defaults", "to_vary_LHS", "to_vary_FF")%in%names(design_info))
all_vars <- design_info$variables
vars_to_vary_LHS <- all_vars[design_info$to_vary_LHS==1]
vars_to_vary_FF  <- all_vars[design_info$to_vary_FF==1]

#Which type of experimental design to generate? 
#As of 2015-05-29, you can generate multiple designs with the single call of the
#script, as long as all the necessary information is provided.

gen_FF  <- TRUE #full factorial
gen_LHS <- TRUE #LHS
points_for_LHS <- "default" #"default" will do points=n dims, or specify integer

#Set base filename for outputs (will be ignored if flags above are false)
#File output gets a stem and then a key (for now, key is just a concatenateation 
#of the timestamp of when exp_design was generated), eg:
#"OAT_exp_20150529-123349.csv"

#FF_out_stem  <- "FF_exp"  #full factorial
#LHS_out_stem <- "LHS_exp" #LHS

#Specify which variables are to be varied as part of the experimental design:
#This are assumed to be coded with a "1" in the input file for "to vary"

################################################################################
#
#   Parameters specific to particular experimental designs:

if(gen_FF){}
#Get the levels for the different variables from a file. The file is assumed to 
#be a csv with column headers specifying the variables and rows specifying the 
#levels for each variable. IT IS OK for the columns to have differing numbers
#of levels, the missing values will be ignored.
FF_params_file <- file.path(exp_dir, "full_factorial_template_prep_shot.csv")

FF_params <- read.csv(FF_params_file)

#Check that all variables have at least one level:
if(any(apply(FF_params, MARGIN=2, FUN=function(x){all(is.na(x))}))){
  stop("Each variable in full factorial design must have at least one level")
}

#check that all variables indicated as FF-related in design_info are actually 
#present in the FF_params table:
if(!all(names(vars_to_vary_FF)%in%names(FF_params))){
  stop("design info file says to include variables in full factorial which do not have their levels set")
}

#Latin hypercube:
use_optimum_LHS <- FALSE  #Optimum results in slightly better space-filling, but 
                          #can take a long time to generate and or crash
#if(gen_LHS)
#Get Latin hypercube bounds:

#to compute depending on the number of runs and number of dimensions.
#options are TRUE, FALSE, and maybe a future option of auto. 

seedLHS <- TRUE
LHSseed <- 1.23456789 #If using randomLHS, can set the seed to reproduce same
                      #design for testing purposes.

################################################################################
####
####  Full factorial
####
################################################################################

if(gen_FF){
  
  #### Full factoral:
  #Convert data frame to list so it can be passed to native function 
  FF_param_list <- as.list(FF_params)
  
  #strip NAs that resulted because some factors have more levels than others:
  FF_param_list <- lapply(FF_param_list, FUN=function(x){x[!is.na(x)]})
  
  FF <- expand.grid(FF_param_list)  

  # Added by HEXG: Remove rows with blank cells (i.e., duplicated rows)
  FF[FF == ""] <- NA
  FF <- FF[complete.cases(FF), ]
  
}

#Get the default habitat target value
#HQ_hab_targ_dt <- as.numeric(as.character(design_info[design_info$variables == 'HQ_hab_targ_DI', 'defaults']))
#Get the FF habitat target values scaled by multipliers
#HQ_hab_targ_FF <- HQ_hab_targ_dt*FF$HQ_hab_multiplier
#FF$HQ_hab_targ_DI <- HQ_hab_targ_FF
#FF$HQ_hab_targ_GS <- HQ_hab_targ_FF
#FF$HQ_hab_targ_MC <- HQ_hab_targ_FF
#FF$HQ_hab_targ_VMM <- HQ_hab_targ_FF
#FF$HQ_hab_targ_DNN <- HQ_hab_targ_FF

################################################################################
#### 
#### Latin hypercube
####
################################################################################

if(gen_LHS){

#All values grabbed as part of design_info, so make sure the file that's 
#reading in accurately reflects the design you want!
  
#Defaults values:
defaults_vec <- design_info$defaults
names(defaults_vec) <- design_info$variables

#Specify the subset for LHS:
vars_to_vary_LHS <- design_info$variables[which(design_info$to_vary_LHS==1)]
#NB: using which() is robust to whether the non-1 values are NA or not.
n_dims <- length(vars_to_vary_LHS)

#if(points_for_LHS=="default"){
#  n_points <- length(vars_to_vary_LHS)
#} else {
#  n_points <- points_for_LHS 
#}



#Now actually create the components:
#### LHS:
if(use_optimum_LHS){
  theLHS_norm <- optimumLHS(n=n_points, k=n_dims, maxSweeps=2, eps=.1, verbose=FALSE)
} else {
  if(seedLHS){ #May be able to drop this construct and just feed preserveDraw
    set.seed(LHSseed)
    theLHS_norm <- randomLHS(n=n_points, k=n_dims, preserveDraw=seedLHS)
  } else {
    theLHS_norm <- randomLHS(n=n_points, k=n_dims)
  }
}

#Convert to data frame and align names:
theLHS_norm <- as.data.frame(theLHS_norm)
names(theLHS_norm) <- vars_to_vary_LHS

#Now scale to bounds as identified in exp_design_file
theLHS <- theLHS_norm
theLHS[] <- NA #Just to make diagnosis of failed population of cells easier.
for(i in vars_to_vary_LHS){
  lb <- design_info$LHS_lower_bound[design_info$variables==i]
  ub <- design_info$LHS_upper_bound[design_info$variables==i]
  theLHS[,i] <- lb + theLHS_norm[, i]*(ub-lb)
}

# For boundary_pen, as we initially sample in the log10 space, now transform back
# theLHS$boundary_pen <- 10**theLHS$boundary_pen - 1

#### IF NOT CROSSING WITH ANYTHING ELSE:
#### NOTE this code chunk can be generalized and moved to other parts too:
rest_of_vars <- all_vars[!all_vars%in%vars_to_vary_LHS]
rest_of_vars_df <- as.data.frame(matrix(design_info$defaults[design_info$variables%in%rest_of_vars],
                                        nrow=nrow(theLHS), 
                                        ncol=length(rest_of_vars),
                                        byrow=TRUE))

names(rest_of_vars_df) <- rest_of_vars

full_design <- cbind(run_num=1:nrow(theLHS), theLHS, rest_of_vars_df)

#export_name <- paste(LHS_out_stem, paste(batch_key, ".csv", sep=""), sep="_")
#write.csv(full_design, file=paste(exp_dir, export_name, sep="/"), 
#          row.names=FALSE)

}

#Little helper thing: If want to be centered around 1 but also want to gen 
#LHS by specifying a maximum ratio ("mult") of factor weights, you are trying to solve
#this system of eqns:
#(lb+ub)/2 = 1 ... ub=mult*lb
#(mult+1)*lb=2
#lb = 2/(mult+1), ub=mult*ub [aka, 2*mult/(mult+1)]

################################################################################
####
####  CROSSING TWO DESIGNS
#Cross the LHS and full-factorial

#BAH! Dumb slow way for now:
for (i in 1:nrow(FF)){
  if (i ==1){
    varying_design <- cbind(theLHS, FF[i,]) #Not sure this is robust to multi-col FF
  } else {
    varying_design <- rbind(varying_design, cbind(theLHS, FF[i,]))
  }
}

#Correct col names from FF (ideally make it so this isn't necessary...)
names(varying_design)[(length(theLHS)+1):length(varying_design)] <- names(FF)

#Now "splice" columns back into the full matrix that may include 
#unchanged values:

#Create a df full of default values with number of rows equal to exp design, 
#and then sub in columns to be replaced:
full_design <- as.data.frame(matrix(NA, nrow=nrow(varying_design), ncol=length(all_vars)))
names(full_design) <- all_vars

#This can probably be done smarter with %in%...
for (i in 1:length(all_vars)){
  active_var <- as.character(all_vars[i])
  if(active_var%in%names(varying_design)){
    full_design[, active_var] <- varying_design[, active_var]
  } else {
    #Assign default value to entire column
    full_design[, active_var] <- defaults_vec[active_var]
  }
}

stopifnot(!any(is.na(full_design)))

#Add in row for defaults?
#full_design <- rbind(defaults_vec, full_design)

#add row numbers as scenario ID:
full_design$scen_id <- paste0('s', 1:nrow(full_design))          
#move scen_id to the first column
full_design <- full_design[, c(ncol(full_design),1:(ncol(full_design)-1))]

write.csv(full_design, file=paste(exp_dir, export_name, sep="/"),
          row.names=FALSE)

