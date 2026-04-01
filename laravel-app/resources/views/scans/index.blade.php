@extends('layouts.app')

@section('title', 'Scans')

@section('content')

<div class="flex items-center justify-between mb-6">
    <div>
        <h2 class="text-lg font-semibold text-white">Point Cloud Scans</h2>
        <p class="text-sm text-gray-500">Upload and process BLK360 scans for Tekla / Revit / SDS2 export</p>
    </div>
    <button disabled
            class="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg opacity-50 cursor-not-allowed">
        <svg class="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg>
        Upload Scan
    </button>
</div>

<div class="bg-gray-900 rounded-xl border border-gray-800">
    <div class="px-5 py-4 border-b border-gray-800 flex items-center justify-between text-xs text-gray-500 uppercase tracking-wider">
        <span>Scan / File</span>
        <div class="flex gap-8">
            <span>Size</span>
            <span>Status</span>
            <span>Uploaded</span>
        </div>
    </div>

    {{-- Empty state --}}
    <div class="py-16 text-center">
        <svg class="w-12 h-12 mx-auto text-gray-700 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <p class="text-gray-500 text-sm mb-1">No scans yet</p>
        <p class="text-gray-700 text-xs">Upload feature coming soon — scan processing pipeline in progress</p>
    </div>
</div>

@endsection
