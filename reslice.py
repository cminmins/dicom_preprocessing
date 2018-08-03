import nibabel as nib
from dipy.align.reslice import reslice

CT_image = nib.load('b.nii')
CT_array = CT_image.get_data()
CT_affine = CT_image.affine
CT_zooms = CT_image.header.get_zooms()

MRT2_image = nib.load("a.nii")
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
nib.save(newCT_image, "ce.nii")
nib.save(newT2_image, "nc.nii")