@extends('layouts.app')

@section('title', 'Dashboard')

@section('content')

{{-- Service status bar --}}
<div class="flex items-center gap-3 mb-6 text-xs">
    <span class="text-gray-500 font-medium uppercase tracking-wider">Services</span>
    <span class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-800 {{ $redisUp ? 'text-emerald-400' : 'text-red-400' }}">
        <span class="w-1.5 h-1.5 rounded-full {{ $redisUp ? 'bg-emerald-400' : 'bg-red-400' }}"></span>
        Redis
    </span>
    <span class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-800 {{ $segmenterUp ? 'text-emerald-400' : 'text-red-400' }}">
        <span class="w-1.5 h-1.5 rounded-full {{ $segmenterUp ? 'bg-emerald-400' : 'bg-red-400' }}"></span>
        Segmenter (Python/GPU)
    </span>
    <span class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-800 text-emerald-400">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
        Laravel
    </span>
    <span class="flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-gray-800 text-emerald-400">
        <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
        Horizon
    </span>
</div>

{{-- Stat cards --}}
<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
    <div class="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <p class="text-xs text-gray-500 uppercase tracking-wider mb-1">Queued Jobs</p>
        <p class="text-3xl font-bold text-white">{{ $stats['queued_jobs'] }}</p>
    </div>
    <div class="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <p class="text-xs text-gray-500 uppercase tracking-wider mb-1">Failed Jobs</p>
        <p class="text-3xl font-bold {{ $stats['failed_jobs'] > 0 ? 'text-red-400' : 'text-white' }}">{{ $stats['failed_jobs'] }}</p>
    </div>
    <div class="bg-gray-900 rounded-xl border border-gray-800 p-5">
        <p class="text-xs text-gray-500 uppercase tracking-wider mb-1">Users</p>
        <p class="text-3xl font-bold text-white">{{ $stats['users'] }}</p>
    </div>
</div>

{{-- Upload CTA --}}
<div class="bg-gray-900 rounded-xl border border-dashed border-gray-700 p-10 text-center mb-8">
    <svg class="w-10 h-10 mx-auto text-gray-600 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"/>
    </svg>
    <p class="text-gray-400 font-medium mb-1">Upload a BLK360 scan</p>
    <p class="text-xs text-gray-600 mb-4">E57 · LAS · LAZ — max 4 GB</p>
    <a href="{{ route('scans.index') }}"
       class="inline-block px-5 py-2 bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium rounded-lg transition">
        Go to Scans
    </a>
</div>

{{-- Quick links --}}
<div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
    <a href="/horizon" target="_blank"
       class="flex items-center gap-2 bg-gray-900 border border-gray-800 rounded-lg px-4 py-3 text-gray-400 hover:text-white hover:border-gray-700 transition">
        <svg class="w-4 h-4 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
        Horizon Dashboard
    </a>
    <a href="http://localhost:8001/docs" target="_blank"
       class="flex items-center gap-2 bg-gray-900 border border-gray-800 rounded-lg px-4 py-3 text-gray-400 hover:text-white hover:border-gray-700 transition">
        <svg class="w-4 h-4 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
        Segmenter API Docs
    </a>
</div>

@endsection
