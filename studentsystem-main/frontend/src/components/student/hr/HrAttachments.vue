<template>
  <div class="hr-page">
    <n-card title="人事附件归档">
      <n-form inline :model="form" class="upload-form">
        <n-form-item label="材料类型">
          <n-select v-model:value="form.attachmentType" :options="typeOptions" style="width: 180px" />
        </n-form-item>
        <n-form-item label="材料名称">
          <n-input v-model:value="form.title" placeholder="如：硕士学位证书" />
        </n-form-item>
        <n-upload :custom-request="uploadFile" :show-file-list="false">
          <n-button type="primary">上传归档</n-button>
        </n-upload>
      </n-form>
      <n-data-table :columns="columns" :data="rows" :loading="loading" />
    </n-card>
  </div>
</template>

<script setup lang="ts">
import { h, onMounted, reactive, ref } from 'vue'
import { NButton, useMessage } from 'naive-ui'
import { getFileUrl, getHrAttachments, uploadHrAttachment } from '@/api'

const message = useMessage()
const loading = ref(false)
const rows = ref<any[]>([])
const form = reactive({ attachmentType: '学历证书', title: '' })
const typeOptions = ['学历证书', '学位证书', '职业资格证', '聘用合同', '培训证明', '职称证书', '岗位聘任文件', '其他材料'].map(value => ({ label: value, value }))

const columns = [
  { title: '材料类型', key: 'attachment_type' },
  { title: '材料名称', key: 'title' },
  { title: '文件名', key: 'original_filename' },
  { title: '上传时间', key: 'created_at' },
  {
    title: '操作',
    key: 'actions',
    render(row: any) {
      return h(NButton, { size: 'small', onClick: () => window.open(getFileUrl(row.file_url), '_blank') }, { default: () => '查看' })
    }
  }
]

async function loadRows() {
  loading.value = true
  try {
    rows.value = await getHrAttachments()
  } finally {
    loading.value = false
  }
}

async function uploadFile({ file, onFinish, onError }: any) {
  if (!form.title) {
    message.warning('请先填写材料名称')
    onError()
    return
  }
  try {
    await uploadHrAttachment(file.file, form.attachmentType, form.title)
    message.success('附件已归档')
    form.title = ''
    await loadRows()
    onFinish()
  } catch (error) {
    onError()
  }
}

onMounted(loadRows)
</script>

<style scoped>
.hr-page { padding: 20px; }
.upload-form { margin-bottom: 16px; }
</style>
