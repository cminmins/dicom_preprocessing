import nibabel as nib
import os.path
import glob
from dipy.align.reslice import reslice
import subprocess
import pydicom

### 파일이 들어있는 폴더 / 원하는 폴더명으로 수정
INPUT_FOLDER = "C:\\Users\\sungmin\\Desktop\\701-702"
output_folder = "C:\\Users\\sungmin\\Desktop\\701-702_reslice"
search_dir = os.listdir(INPUT_FOLDER)
print(search_dir)

### 폴더구성은 CT와 MRI\\T2로 되어있음. 별도로 수정해도됨
for i in search_dir:
    current_dir = INPUT_FOLDER + '\\' + i
    path_ct = current_dir + "\\CT"
    path_t2 = current_dir + "\\MRI\\T2"


    ## 해당 폴더에 가장 첫번째 파일로 맞추기 위해서
    ct_default = glob.glob(os.path.join(path_ct, "*.dcm"))
    ct_default_first = pydicom.dcmread(ct_default[0])
    mr_default = glob.glob(os.path.join(path_t2, "*.dcm"))
    mr_default_first = pydicom.dcmread(mr_default[0])


    #####  여러가지의 Series를 하나의 Series로 합치기 위한 헤더 수정작업
    index = 0
    for a in ct_default:
        ds = pydicom.dcmread(a)
        ds.SeriesInstanceUID = '12345'
        try:
            ds.SeriesDescription = "Spine"
        except:
            print(path_ct)
        ds.InstanceCreationTime = "0"
        ds.SeriesTime = "0"
        ds.InstanceNumber = index
        ds.SeriesNumber = 0
        try:
            ds.ImageOrientationPatient = ct_default_first.ImageOrientationPatient
        except:
            print(path_ct)
        index += 1
        pydicom.dcmwrite(a, ds)

    for a in mr_default:
        ds = pydicom.dcmread(a)
        ds.SeriesInstanceUID = '12345'
        try:
            ds.SeriesDescription = "Spine"
        except:
            print(path_t2)
        ds.InstanceCreationTime = "0"
        ds.SeriesTime = "0"
        ds.InstanceNumber = index
        ds.SeriesNumber = 0
        try:
            ds.ImageOrientationPatient = mr_default_first.ImageOrientationPatient
        except:
            print(path_t2)
        index += 1
        pydicom.dcmwrite(a, ds)

    # dcm2nii 실행하는 코드(dicom -> nii) / Popen의 인자값은 dcm2nii의 위치로 수정하면됨,
    print("start dcm2nii")
    sub_ct = subprocess.Popen(["C:\\Users\\sungmin\\Desktop\\dicom2nii\\dcm2nii.exe", path_ct], stdout=subprocess.PIPE)
    print(sub_ct.stdout.read())  # Deadlock
    sub_mr = subprocess.Popen(["C:\\Users\\sungmin\\Desktop\\dicom2nii\\dcm2nii.exe", path_t2], stdout=subprocess.PIPE)
    print(sub_mr.stdout.read())  # Deadlock

    ###해당 경로에서 .nii 확장자 찾기(절대경로로 저장됨)
    ct_file = glob.glob(os.path.join(path_ct, "*.nii"))
    t2_file = glob.glob(os.path.join(path_t2, "*.nii"))
    # print(ct_file[0])
    # print(t2_file[0])

    # ################# Resllice 코드 ########################

    ### CT read
    CT_image = nib.load(ct_file[0])
    CT_array = CT_image.get_data()
    CT_affine = CT_image.affine
    CT_zooms = CT_image.header.get_zooms()

    ### MRI read
    MRT2_image = nib.load(t2_file[0])
    MRT2_array = MRT2_image.get_data()
    MRT2_affine = MRT2_image.affine
    MRT2_zooms = MRT2_image.header.get_zooms()

    ### CT의 zoom 수정
    CT_zooma = CT_image.header['dim'][1] / MRT2_image.header['dim'][1] * CT_zooms[0]
    CT_zoomb = CT_image.header['dim'][2] / MRT2_image.header['dim'][2] * CT_zooms[1]
    CT_zoomc = CT_image.header['dim'][3] / MRT2_image.header['dim'][3] * CT_zooms[2]

    ### CT의 바뀐 zoom 적용
    change_zoomCT_L = [CT_zooma, CT_zoomb, CT_zoomc]
    change_zoomCT = tuple(change_zoomCT_L)

    ### 수정된 zoom으로 Reslice
    newCT_brain, newCT_affine = reslice(CT_array, CT_affine, CT_zooms , change_zoomCT)
    newT2_brain, newT2_affine = reslice(MRT2_array, MRT2_affine, MRT2_zooms, MRT2_zooms)

    ### Reslice한 파일 저장
    newCT_image = nib.Nifti1Image(newCT_brain, newCT_affine)
    newT2_image = nib.Nifti1Image(newT2_brain, newT2_affine)
    out_ct = output_folder + "\\" + i + "\\CT"
    out_mr = output_folder + "\\" + i + "\\MRI"
    os.mkdir(output_folder + "\\" + i)
    os.mkdir(out_ct)
    os.mkdir(out_mr)
    nib.save(newCT_image, out_ct + "\\Reslice_ct_" + i + ".nii")
    nib.save(newT2_image, out_mr + "\\Reslice_mri_" + i + ".nii")

    ### Nii 파일 -> Dicom + split3d
    env_path = os.environ
    med_split = subprocess.Popen(["medcon", "-f", "*.nii", "-c", "dicom", "-split3d", "-n", "-qc", "-rs", "-fv"], stdout=subprocess.PIPE, env=env_path, cwd=out_ct)
    print(med_split.stdout.read())
    med_split = subprocess.Popen(["medcon", "-f", "*.nii", "-c", "dicom", "-split3d", "-n", "-qc", "-rs", "-fv"], stdout=subprocess.PIPE, env=env_path, cwd=out_mr)
    print(med_split.stdout.read())
