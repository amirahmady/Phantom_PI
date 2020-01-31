clear all;
clc; 
addpath ('/media/sawant/Maida/MotionDataAnd4DPhantomManual/make_trajectories/mat_lib/'); 

%%%%%%%%%%%%%%
%location of matfiles
mat_src='/media/sawant/Maida/MotionDataAnd4DPhantomManual/trajectories/phantom_confirmed/'; 
src_output=sprintf('/media/sawant/Maida/MotionDataAnd4DPhantomManual/trajectories/traj_amp%4.2f_deadt%d_tcut%d_tramp%d/', amp_scale(1), T_dead, t_cuts, T_ramp); 

if (~exist(src_output))
    mkdir(src_output); 
end


%src_traj=sprintf('/media/sawant/Maida/MotionDataAnd4DPhantomManual/trajectories/trajectories_%4.2f_w_dead_X/', amp_scale(1)); 
%src_png='/media/sawant/Maida/MotionDataAnd4DPhantomManual/png/'; 
%if (~exist(src_png))
%    mkdir(src_png); 
%end
%if (~exist(src_traj))
%    mkdir(src_traj); 
%end

%read list of files and remove . and .. directories from list
files=dir(mat_src); 
isub=~[files(:).isdir]; 
files=files(isub); 
matfiles={}; 
for i= 1:length(files)
    fname=files(i).name;
    tmp= strsplit(fname, '.');
    if (strcmp(tmp(2),'mat'))
        matfiles{end+1}= sprintf ('%s',fname);               
    end

end

%fid=fopen(sprintf('%slist.txt', src_traj), 'w+');
for ifile=22 %length(matfiles)
     tmp_mfile =load(sprintf('%s%s', mat_src, matfiles{ifile}));

     coord=tmp_mfile.DataPatientCoordinate; 
     time=tmp_mfile.timeData*t_scale; 

    %shave off large deviations from the baseline
    %tolerance is set to mean +/- NTOL*std
    for idim=1:3
          coord(idim, :)=coord(idim, :)-mean(coord(idim, :)); 
          mean_p = mean(coord(idim, :)); 
          std_p = std(coord(idim, :)); 
          upper = mean_p + NTOL*std_p; 
          lower = mean_p - NTOL*std_p; 
          coord(idim, find(coord(idim, :)>upper))=upper; 
          coord(idim, find(coord(idim, :)<lower))=lower; 
          coord(idim, :)=medfilt1(squeeze(coord(idim, :)), Nfilt_time); 
          coord(idim, :)=fastsmooth(coord(idim, :), 30); 
    end
    
    time=time - time(1); 
    dt_data = time(2) - time(1); 
    %index for  how long to read
    ind_end = min(length(time)-Nfilt_time, T_end / dt_data); 
    ind_end = round(ind_end); 
    time_zero = time(1:ind_end); 
    coord = coord(:, 1:ind_end); 

    %scale the trajectory based on desired scaling
    scaling=[]; 
    for idim=1:3
        scaling(idim) = max(coord(idim, :)) - min(coord(idim, :)); 
        scaling(idim) = abs(scaling(idim)); 
        scaling(idim) = amp_scale(idim) / scaling(idim); 
        txt_disp=sprintf('scaling %d dimension = %f',idim, scaling(idim));  
        disp(txt_disp); 
    end
       
    
    %interpolate data to motion platform time coordinate
    data_mp =[]; 
    time_mp = time(1) : dT_motionplatform:time(ind_end); 
    for idim=1:3
        data_mp(idim, :) = interp1(time_zero, coord(idim, :), time_mp) * scaling(idim); 
    end
        
    if (cuts_flag)
        out_loc=sprintf('%s%s/', src_output, strrep(strrep(matfiles{ifile}, '.mat', ''), ' ', '_')); 
        if(~exist(out_loc))
            mkdir(out_loc); 
        end
        cut_data(time_mp, data_mp, t_cuts, T_ramp, T_dead, dT_motionplatform, out_loc); 
    end
    
    
    
end
        
        
    