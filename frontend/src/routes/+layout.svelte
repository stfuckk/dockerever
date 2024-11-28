<script>
    import '../app.css';
    import NavigationBar from '$lib/global/NavigationBar.svelte';

    let { children } = $props();
</script>

{@render children()}

<NavigationBar></NavigationBar>